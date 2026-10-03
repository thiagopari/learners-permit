# GR00T offline fix (applied on this drive, 2026-10-03)

GR00T N1.7 loads its Cosmos-Reason2-2B processor through transformers 4.57.3, which always calls the
Hugging Face website (`model_info`, to check whether a model is "based on Mistral") when a model is
named by repo id, even when every file is cached. With no internet, or with `HF_HUB_OFFLINE=1`, the
GR00T policy server fails while loading its processor. A local folder path skips that call.

What was changed:

- `hf/local/nvidia/Cosmos-Reason2-2B` is a link to the cached Cosmos snapshot. The path has to contain
  `nvidia/Cosmos-Reason2`, because GR00T picks its backbone class by that substring.
- In both checkpoints (`ckpt/GR00T-N1.7-LIBERO/libero_10` and `libero_goal`), `model_name` in
  `config.json` and `processor_kwargs.model_name` in `processor_config.json` now point to
  `/hf/local/nvidia/Cosmos-Reason2-2B`, which is where the cell container sees that link
  (the box's `~/.cache/huggingface` is mounted at `/hf`).
- The originals are kept as `config.json.orig` and `processor_config.json.orig`. To revert, copy them back.

Verified under emulation, with the network disabled and `HF_HUB_OFFLINE=1`: both checkpoints load
their config, select `Qwen3Backbone`, and load `Gr00tN1d7Processor`.

NemoClaw's vLLM image uses transformers 5.6, which no longer makes that call, so Qwen is not affected.
If you serve Cosmos with vLLM for failure diagnosis, pass the local snapshot path as the model.
