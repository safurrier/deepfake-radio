create-conda-env:
	conda create --name deepfake_radio python=3.11 -y

requirements:
	pip install -r requirements.txt

run:
	python main.py