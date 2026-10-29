"""Train a leaf classifier on PlantVillage, never on the photos the licence is tested on.

    python crop/train.py --data DIR --exclude docs/results/crop-dataset-manifest.json --out models/leaf

DIR holds PlantVillage class folders (Tomato___healthy, ...). Every photo listed in the manifest (the few-shot run's
references and its 140 trial photos) is excluded by SHA-256, so the trained model is commissioned on exactly the photos
the few-shot model was, and has never seen them. Fine-tunes an ImageNet-pretrained ResNet-18 (torchvision) on the
five crop/diagnosis classes in crop.leaf.CROPS. Writes model.pt, its SHA-256, and training_meta.json.
"""
import argparse
import hashlib
import json
import pathlib
import random
import sys
import time

import torch
import torchvision
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from crop.leaf import CROPS  # noqa: E402

CLASSES = [f"{crop}:{label}" for crop, labels in CROPS.items() for label in labels]  # e.g. "tomato:late_blight"
FOLDER = {folder: f"{crop}:{label}" for crop, labels in CROPS.items() for label, folder in labels.items()}
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]


def transform(train):
    t = [torchvision.transforms.Resize((224, 224))]
    if train:
        t += [torchvision.transforms.RandomHorizontalFlip(), torchvision.transforms.RandomVerticalFlip(),
              torchvision.transforms.ColorJitter(0.2, 0.2, 0.2)]
    return torchvision.transforms.Compose(t + [torchvision.transforms.ToTensor(), torchvision.transforms.Normalize(MEAN, STD)])


class Leaves(Dataset):
    def __init__(self, items, train):
        self.items, self.t = items, transform(train)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        path, y = self.items[i]
        return self.t(Image.open(path).convert("RGB")), y


def collect(data, exclude):
    """(path, class index) for every photo not in the exclusion manifest, and how many were excluded."""
    held_out = {row["sha256"] for row in json.load(open(exclude))}
    items, skipped = [], 0
    for folder, cls in FOLDER.items():
        for p in sorted((pathlib.Path(data) / folder).iterdir()):
            if hashlib.sha256(p.read_bytes()).hexdigest() in held_out:
                skipped += 1
                continue
            items.append((p, CLASSES.index(cls)))
    return items, skipped


def model_for(n):
    m = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)
    m.fc = nn.Linear(m.fc.in_features, n)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--exclude", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=int, default=4)
    a = ap.parse_args()
    torch.manual_seed(0)
    items, skipped = collect(a.data, a.exclude)
    random.Random(0).shuffle(items)
    n_val = len(items) // 10
    val, train = items[:n_val], items[n_val:]
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = model_for(len(CLASSES)).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()
    tl = DataLoader(Leaves(train, True), batch_size=64, shuffle=True, num_workers=8)
    vl = DataLoader(Leaves(val, False), batch_size=128, num_workers=8)
    history, t0 = [], time.time()
    for epoch in range(a.epochs):
        model.train()
        for x, y in tl:
            opt.zero_grad()
            with torch.autocast(dev, dtype=torch.bfloat16, enabled=dev == "cuda"):
                loss = loss_fn(model(x.to(dev)), y.to(dev))
            loss.backward()
            opt.step()
        model.eval(); right = 0
        with torch.no_grad():
            for x, y in vl:
                right += (model(x.to(dev)).argmax(1).cpu() == y).sum().item()
        history.append({"epoch": epoch + 1, "val_accuracy": round(right / len(val), 4), "loss": round(loss.item(), 4)})
        print(json.dumps(history[-1]), flush=True)
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.state_dict(), "classes": CLASSES, "arch": "resnet18"}, out / "model.pt")
    sha = hashlib.sha256((out / "model.pt").read_bytes()).hexdigest()
    meta = {"arch": "resnet18, ImageNet-pretrained (torchvision IMAGENET1K_V1), fine-tuned", "classes": CLASSES,
            "train_photos": len(train), "val_photos": len(val), "excluded_held_out_photos": skipped,
            "epochs": a.epochs, "history": history, "minutes": round((time.time() - t0) / 60, 1),
            "device": torch.cuda.get_device_name(0) if dev == "cuda" else "cpu", "model_sha256": sha}
    json.dump(meta, open(out / "training_meta.json", "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("train_photos", "excluded_held_out_photos", "minutes", "model_sha256")}))


if __name__ == "__main__":
    main()
