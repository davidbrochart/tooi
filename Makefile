run:
	textual run --dev tooi.cli:main

dist:
	python -m build

publish :
	twine upload dist/*.tar.gz dist/*.whl

clean:
	rm -rf dist
