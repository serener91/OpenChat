# ubuntu:latest

# Install latest vllm
git clone https://github.com/vllm-project/vllm.git
cd vllm
VLLM_USE_PRECOMPILED=1 pip install --editable .

# Install latest transformers
pip install git+https://github.com/huggingface/transformers.git


nohup bash model_setting.sh &> log.out &


python -c "import torch; print(torch.version.cuda)"