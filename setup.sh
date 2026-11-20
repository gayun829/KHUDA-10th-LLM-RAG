#!/usr/bin/env bash
# EC2 (Ubuntu)에서 한 번 실행 : 가상환경(.venv)을 만들고 패키지를 설치한다.
#   bash setup.sh
set -e
cd "$(dirname "$0")"

if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  echo "[1/3] python3-venv 설치 (sudo apt) ..."
  sudo apt-get -o DPkg::Lock::Timeout=180 update -qq
  sudo apt-get -o DPkg::Lock::Timeout=180 install -y -qq python3-venv >/dev/null
fi

echo "[2/3] 가상환경 .venv 만들기 ..."
python3 -m venv .venv
. .venv/bin/activate

echo "[3/3] 패키지 설치 (openai, numpy, python-dotenv, fastapi, uvicorn) ..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

[ -f .env ] || cp .env.example .env
python -c "import openai, numpy, fastapi; print('설치 완료 : Python', __import__('sys').version.split()[0], '/ openai', openai.__version__, '/ numpy', numpy.__version__, '/ fastapi', fastapi.__version__)"
echo
echo "다음 순서 :"
echo "  1) source .venv/bin/activate      ← 터미널을 새로 열 때마다"
echo "  2) nano .env                      ← OPENAI_API_KEY=sk-... 입력 (저장 Ctrl+O, Enter / 나가기 Ctrl+X)"
echo "  3) python step0_check.py"
