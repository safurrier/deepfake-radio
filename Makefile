create-conda-env:
	conda create --name deepfake_radio python=3.11 -y

requirements:
	# pip install -r requirements.txt
	pip install -e .

run:
	python main.py