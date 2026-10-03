# Runtime configuration on the GB10 (captured 2026-10-03)

How the containers were actually launched on the Dell Pro Max GB10 during the hackathon. Environment variable values are deliberately not recorded.

## Containers

### `vllm-qwen`

- Image: `nvcr.io/nvidia/vllm:26.05.post1-py3`
- Network: `bridge`, IPC: `host`, GPU access: `True`, shm: `67108864`
- Entrypoint: `["/opt/nvidia/nvidia_entrypoint.sh"]`
- Command:

```
vllm serve nvidia/Qwen3.6-35B-A3B-NVFP4 --trust-remote-code --kv-cache-dtype fp8 --attention-backend flashinfer --moe-backend marlin --gpu-memory-utilization 0.5 --max-model-len 262144 --max-num-seqs 8 --max-num-batched-tokens 8192 --enable-chunked-prefill --async-scheduling --enable-prefix-caching --language-model-only --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3
```
- Mounts: `/home/dell/.cache/huggingface -> /root/.cache/huggingface`
- Environment variable names (values not recorded): BASH_ENV, CPATH, CUBLASMP_VERSION, CUBLAS_VERSION, CUDA_ARCH_LIST, CUDA_COMPONENT_LIST, CUDA_DRIVER_VERSION, CUDA_HOME, CUDA_VERSION, CUDLA_VERSION, CUDNN_FRONTEND_VERSION, CUDNN_VERSION, CUFFT_VERSION, CUFILE_VERSION, CURAND_VERSION, CUSOLVERMP_VERSION, CUSOLVER_VERSION, CUSPARSELT_VERSION, CUSPARSE_VERSION, CUTILE_PYTHON_VERSION, CUTLASS_DSL_VERSION, DALI_BUILD, DALI_URL_SUFFIX, DALI_VERSION, DOCA_VERSION, EFA_VERSION, ENV, GDRCOPY_VERSION, HF_HUB_OFFLINE, HPCX_VERSION, LD_LIBRARY_PATH, LIBRARY_PATH, MAXSMVER, MAX_JOBS, MODEL_OPT_VERSION, MOFED_VERSION, NCCL_VERSION, NIXL_VERSION, NPP_VERSION, NSIGHT_COMPUTE_VERSION, NSIGHT_SYSTEMS_VERSION, NVFATBIN_VERSION, NVIDIA_BUILD_ID, NVIDIA_DRIVER_CAPABILITIES, NVIDIA_PRODUCT_NAME, NVIDIA_REQUIRE_CUDA, NVIDIA_VISIBLE_DEVICES, NVIDIA_VLLM_VERSION, NVJITLINK_VERSION, NVJPEG_VERSION, NVPTXCOMPILER_VERSION, NVRX_VERSION, NVSHMEM_VERSION, NVVM_VERSION, OMPI_MCA_coll_hcoll_enable, OPAL_PREFIX, OPENMPI_VERSION, OPENUCX_VERSION, PATH, PIP_BREAK_SYSTEM_PACKAGES, PIP_CONSTRAINT, PIP_NO_BUILD_ISOLATION, POLYGRAPHY_VERSION, PYTORCH_TRITON_VERSION, RDMACORE_VERSION, SHELL, TIKTOKEN_CACHE_DIR, TIKTOKEN_RS_CACHE_DIR, TORCH_CUDA_ARCH_LIST, TRANSFORMER_ENGINE_VERSION, TRITON_CUDACRT_PATH, TRITON_CUDART_PATH, TRITON_CUOBJDUMP_PATH, TRITON_CUPTI_PATH, TRITON_NVDISASM_PATH, TRITON_PTXAS_PATH, TRTOSS_VERSION, TRT_VERSION, VLLM_FLASH_ATTN_SRC_DIR, VLLM_VERSION, _CUDA_COMPAT_PATH

### `cell`

- Image: `hack/cell`
- Network: `host`, IPC: `host`, GPU access: `True`, shm: `67108864`
- Entrypoint: `null`
- Command:

```
sleep infinity
```
- Mounts: `/home/dell/hack/ckpt -> /ckpt`, `/home/dell/.cache/huggingface -> /hf`, `/home/dell/hack/src/app -> /app`
- Environment variable names (values not recorded): CPATH, CPLUS_INCLUDE_PATH, CUDA_HOME, CUDA_PATH, CUDA_VERSION, C_INCLUDE_PATH, DEBIAN_FRONTEND, DOCKER_CONTAINER, HF_HOME, HF_HUB_OFFLINE, LD_LIBRARY_PATH, LIBRARY_PATH, MUJOCO_GL, NCCL_VERSION, NO_ALBUMENTATIONS_UPDATE, NVARCH, NVIDIA_DRIVER_CAPABILITIES, NVIDIA_PRODUCT_NAME, NVIDIA_REQUIRE_CUDA, NVIDIA_VISIBLE_DEVICES, NV_CUDA_CUDART_DEV_VERSION, NV_CUDA_CUDART_VERSION, NV_CUDA_LIB_VERSION, NV_CUDA_NSIGHT_COMPUTE_DEV_PACKAGE, NV_CUDA_NSIGHT_COMPUTE_VERSION, NV_LIBCUBLAS_DEV_PACKAGE, NV_LIBCUBLAS_DEV_PACKAGE_NAME, NV_LIBCUBLAS_DEV_VERSION, NV_LIBCUBLAS_PACKAGE, NV_LIBCUBLAS_PACKAGE_NAME, NV_LIBCUBLAS_VERSION, NV_LIBCUSPARSE_DEV_VERSION, NV_LIBCUSPARSE_VERSION, NV_LIBNCCL_DEV_PACKAGE, NV_LIBNCCL_DEV_PACKAGE_NAME, NV_LIBNCCL_DEV_PACKAGE_VERSION, NV_LIBNCCL_PACKAGE, NV_LIBNCCL_PACKAGE_NAME, NV_LIBNCCL_PACKAGE_VERSION, NV_LIBNPP_DEV_PACKAGE, NV_LIBNPP_DEV_VERSION, NV_LIBNPP_PACKAGE, NV_LIBNPP_VERSION, NV_NVML_DEV_VERSION, NV_NVTX_VERSION, PATH, PYOPENGL_PLATFORM, TRITON_PTXAS_PATH, UV_LINK_MODE, UV_NO_CACHE, UV_PROJECT_ENVIRONMENT, VIRTUAL_ENV

### Processes inside `cell`

```
bash -c python gr00t/eval/run_gr00t_server.py --model-path /ckpt/GR00T-N1.7-LIBERO/libero_10 --embodiment-tag LIBERO_PANDA --use-sim-policy-wrapper --host 127.0.0.1 --port 5555 > /tmp/gr00t_libero_10.log 2>&1
python gr00t/eval/run_gr00t_server.py --model-path /ckpt/GR00T-N1.7-LIBERO/libero_10 --embodiment-tag LIBERO_PANDA --use-sim-policy-wrapper --host 127.0.0.1 --port 5555
bash -c python gr00t/eval/run_gr00t_server.py --model-path /ckpt/GR00T-N1.7-LIBERO/libero_goal --embodiment-tag LIBERO_PANDA --use-sim-policy-wrapper --host 127.0.0.1 --port 5556 > /tmp/gr00t_libero_goal.log 2>&1
python gr00t/eval/run_gr00t_server.py --model-path /ckpt/GR00T-N1.7-LIBERO/libero_goal --embodiment-tag LIBERO_PANDA --use-sim-policy-wrapper --host 127.0.0.1 --port 5556
```


## NemoClaw network policies (sandbox `navfix`)

● = enabled

```

  Policy presets for sandbox 'navfix':
    ○ brave — Brave Search API access
    ● brew [user-added] — Homebrew (Linuxbrew) package manager access (brew binary preinstalled in base image)
    ○ claude-code — Claude Code API, browser login, telemetry, and crash-report access
    ○ github — GitHub.com and GitHub API access (git)
    ○ gmail — Gmail IMAP and SMTP access for Python App Password workflows
    ● huggingface [user-added] — Hugging Face Hub, LFS, and Inference API access
    ○ jira — Jira and Atlassian Cloud access
    ● local-inference [user-added] — Local inference access (Ollama, vLLM, llama.cpp) through the OpenShell gateway
    ○ local-memory — Local Hindsight memory service access through the OpenShell gateway
    ○ nous-audio — Nous Portal managed audio generation and transcription gateway
    ○ nous-browser — Nous Portal managed browser automation gateway
    ○ nous-code — Nous Portal managed sandboxed code execution gateway
    ○ nous-image — Nous Portal managed image generation gateway
    ○ nous-web — Nous Portal managed web search and crawl gateway
    ● npm [user-added] — npm and Yarn registry access
    ○ observability-otlp-local — OTLP/HTTP trace export to a local host collector
    ○ openclaw-diagnostics-otel-local — OpenClaw diagnostics OTLP/HTTP export to local host collector
    ● openclaw-pricing [from openclaw agent] — OpenClaw model-pricing reference fetch (LiteLLM + OpenRouter)
    ○ outlook — Microsoft Outlook and Graph API access
    ○ personal-open-internet — Broad TCP egress on destination ports 80 and 443 for trusted personal sandboxes
    ○ public-reference — Read-only structured public reference APIs
    ● pypi [user-added] — Python Package Index (PyPI) access
    ○ tavily — Tavily web search API access (opt-in)
    ○ weather — Read-only public weather, geocoding, and alert APIs
    ○ telegram — Telegram Bot API access
    ● discord [user-added] — Discord API, gateway, and CDN access
    ○ wechat — WeChat (personal) iLink API access (OpenClaw + Hermes)
    ○ slack — Slack API, Socket Mode, and webhooks access
```
