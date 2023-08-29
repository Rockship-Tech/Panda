.PHONY: build-image-local
build-image-local:
	docker build --platform linux/amd64 -f builder/Dockerfile -t ${commit} . --build-arg BOT_PRIVATE_TOKEN=${BOT_PRIVATE_TOKEN} --build-arg DEPLOY_TAG=${DEPLOY_TAG}
	docker tag ${commit} ${latest}
	docker push ${latest}
