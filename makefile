REGISTRY ?=
REPOSITORY ?= imlahso/data-side-car:latest

.image:
	docker build -t ${REGISTRY}${REPOSITORY} .

.publish:
	docker build --pull --no-cache -t $ ${REGISTRY}${REPOSITORY} .
	docker push ${REGISTRY}${REPOSITORY}