# LOCAL TRANSCRIPTION API ENDPOINT

This project is about creating an API service that exposes a transcription model (speech to text). 

## Requirements
- Use FastAPI to expose a "/transcribe" endpoint.
- The service must be able to handle multiple requests simultaneously without crashing, e.g. via some kind of queue either explicitly or implicitly.
- Run the service inside one or several Docker containers based on the complexity of the system. Default to a modular microservice architecture if needed.  
- Launch Docker container via Docker compose
- Must be compatible with the CUDA information described in the section "nvidia-smi output". ALternatively, a comprehensive analysis must be made of how to downgrade CUDA to a version compatible with the remaining components in the service. Put this analysis in a separate file and DO NOT EVER downgrade without explicit instructions to do so. Do not ask me if you're allowed to downgrade. I will explicitly instruct you to do so if I deem it necessary based on your analysis.
- MUST use Hviske 2.0 via Huggingface transformers. See `test_hviske.py" for inspiration. 
- The /transcribe endpoint must receive an audio file and return transcriptions. If the underlying transcription model supports it, the following must be returned: 1) A full text transcription, 2) time stamped transcriptions. 
- If the underlying model supports it, the service must include a "detect language" endpoint
- The whole service including model inference and API endpoints will be running on a Fusionxpark with 128GB unified VRAM. 
- VERY IMPORTANT: I must be able to call the endpoint from a different machine that is not necessarily on the same network. That is, from my laptop on a different WiFi, I must be able to call the endpoints running on the FusionXpark. Authenticaion is not a priority. The endpoint can be made open to all to avoid a complex software setup on the FusionXpark. 
- The service is primarily intended for transcription of Danish speech. 
- Allow both long and big audio files. Set liberal limits. 
- We expect low to moderate load on the service. We expect no more than 10 simultaneous requests at any time. 

## Other instructions
- In the planning process, analyze if running multiple model instances will degrade or improve performance over running just one model instance. 

## `nvidia-smi` output
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.126.09             Driver Version: 580.126.09     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GB10                    On  |   0000000F:01:00.0  On |                  N/A |
| N/A   46C    P0             12W /  N/A  | Not Supported          |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A            3038      C   /usr/local/bin/python3                  274MiB |
|    0   N/A  N/A            3981      G   /usr/lib/xorg/Xorg                      207MiB |
|    0   N/A  N/A            4116      G   /usr/bin/gnome-shell                    163MiB |
|    0   N/A  N/A            5755      G   /usr/share/code/code                     90MiB |
|    0   N/A  N/A            8449      G   .../7832/usr/lib/firefox/firefox        228MiB |
+-----------------------------------------------------------------------------------------+

