LIB_DIR = "./lib"

pip:
	@pip install --upgrade -r requirements.txt -t lib

deploy: clean purge
	@if [ ! -d $(LIB_DIR) ]; then make pip; fi
	@/usr/local/bin/appcfg.py update .;

test:
	@py.test --cov=app tests/

clean:
	@find . -name "*.pyc" | xargs rm || true

devrun:
	@dev_appserver.py .;

purge:
	@curl -sS -X DELETE "https://api.cloudflare.com/client/v4/zones/0b803238e147a0096159f908651bcfa5/purge_cache" \
		-H "X-Auth-Email: rodrigodelduca@gmail.com" \
		-H "X-Auth-Key: 81967d28cc4ba49563de94a997a737b76478e" \
		-H "Content-Type: application/json" \
		--data '{"purge_everything":true}' | \
		python -c "import sys, json; assert json.load(sys.stdin)['success'] == True"
