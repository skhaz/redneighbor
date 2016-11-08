clean:
	@rm -rf build bower_components node_modules

deps: bower.json
	@bower install

build: deps
	@polymer build

devrun: deps
	@polymer serve --open

deploy: build purge
	@firebase deploy

purge:
	@curl -sS -X DELETE "https://api.cloudflare.com/client/v4/zones/0b803238e147a0096159f908651bcfa5/purge_cache" \
		-H "X-Auth-Email: rodrigodelduca@gmail.com" \
		-H "X-Auth-Key: 81967d28cc4ba49563de94a997a737b76478e" \
		-H "Content-Type: application/json" \
		--data '{"purge_everything":true}' | \
		python -c "import sys, json; assert json.load(sys.stdin)['success'] == True"
