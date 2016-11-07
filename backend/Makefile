LIB_DIR = "./lib"

pip:
	@pip install --upgrade -r requirements.txt -t lib

deploy:
	@if [ ! -d $(LIB_DIR) ]; then make pip; fi
	@/usr/local/bin/appcfg.py update .;

test:
	@py.test --cov=app tests/

clean:
	@find . -name "*.pyc" | xargs rm || true

devrun:
	@dev_appserver.py .;
