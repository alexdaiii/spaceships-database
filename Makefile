.PHONY = requirements

requirements:
	echo "Creating requirements.txt from poetry.lock"
	poetry export --without-hashes -f requirements.txt -o requirements.txt
