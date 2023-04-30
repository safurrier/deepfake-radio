create-conda-env:
	conda create --name deepfake_radio python=3.11 -y

requirements:
	pip install -r requirements.txt
	chmod +x install_dependencies.sh
	sh install_dependencies.sh
run:
	python main.py