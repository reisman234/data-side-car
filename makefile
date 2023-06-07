REPOSITORY ?= harbor.gx4ki.imla.hs-offenburg.de
APPLICATION ?= gx4ki/data-side-car:latest

.image:
	docker build -t ${REPOSITORY}/${APPLICATION} .

.publish:
	docker build --pull --no-cache -t $ ${REPOSITORY}/${APPLICATION} .
	docker push ${REPOSITORY}/${APPLICATION}
