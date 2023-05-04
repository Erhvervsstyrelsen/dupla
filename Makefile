COMMAND=python
ifdef PYCMD
	COMMAND=$(PYCMD)
endif

package:
	$(COMMAND) -m build

check:
	twine check dist/*

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	pyclean -v .

publish_test:
	make clean
	make package
	make check
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish:
	make clean
	make package
	make check
	twine upload dist/*
