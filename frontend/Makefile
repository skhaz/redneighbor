clean:
	@rm -rf build bower_components node_modules

deps: bower.json
	@bower install

build: deps
	@polymer build

devrun: deps
	@polymer serve --open

deploy: build
	@firebase deploy
