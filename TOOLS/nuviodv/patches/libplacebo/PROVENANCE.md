# libplacebo patches (NuvioDV AnimeJaNai line)

Copied unchanged from `the-database/mpv-winbuild` at commit
`ca38487e28304e4af70de6cee243469883c0f8b5` (repository root), which applies them to
the libplacebo used by the AnimeJaNai Windows builds. They are applied here to the
pinned libplacebo in `../../sources.json`; their SHA-256 digests are recorded there
as `libplacebo_patches` and verified by `sources.py patch` before application.
All four apply cleanly to the pinned commit
`9fabf6d5057c40089afb020017c6347002b07308`.

| Patch | Purpose |
| --- | --- |
| `libplacebo-present-queue.patch` | Present on one queue so presentation order holds while rendering rotates queues. |
| `libplacebo-nvidia-swapchain-recreate.patch` | Windows/NVIDIA: drain the old swapchain before recreation, avoiding a driver wait inside `vkCreateSwapchainKHR` on display-mode changes. |
| `libplacebo-opaque-composite-alpha.patch` | Prefer an opaque swapchain without requested alpha, keeping independent flip/VRR on Windows. |
| `libplacebo-nvidia-rtx-hdr.patch` | Windows/NVIDIA: keep libplacebo queue locks instead of driver-internal queue synchronization (RTX HDR present deadlock). Compiled only when the Vulkan headers define `VK_KHR_internally_synchronized_queues`. |

These are presentation-path changes; they do not alter colour processing. Dolby
Vision output is requalified by `verify-windows.py` for every build.
