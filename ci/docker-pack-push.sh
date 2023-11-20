if [ "$REF" = "refs/heads/main" ]; then
  TAG=latest
elif [[ "$REF"  == refs/tags/* ]]; then
  TAG="${REF#refs/tags/}"
else
  TAG=dev
fi

FULL_TAG="soramitsu/iroha2-mailer-ci:${TAG}"

docker build -t $FULL_TAG .
docker push $FULL_TAG
