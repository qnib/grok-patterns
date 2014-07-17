PKG_NAME="qnib-grok-patterns"
echo "PKG_NAME=${PKG_NAME}"
PKG_VERSION=$(git describe --match "[0-9]*" --abbrev=0 --tags)
TODAY="$(date +'%Y%m%d')"
ITER="1"
REPO_PATH=${REPO_PATH-/tmp/}
OLD_ITER=$(find ${REPO_PATH} -name "${PKG_NAME}-${PKG_VERSION}*"|grep ${TODAY}|awk -F"${TODAY}." '{print $2}'|awk -F\. '{print $1}'|tail -n1)
echo "OLD_ITER=${OLD_ITER}"
if [ "X${OLD_ITER}" != "X" ];then
   ITER=$(echo "${OLD_ITER}+1"|bc)
fi
ARCH="noarch"
FILE="${PKG_NAME}-${PKG_VERSION}-${TODAY}.${ITER}.${ARCH}.rpm"
echo "FILE=${FILE}"
FILE_PATH="${REPO_PATH}/${ARCH}/${FILE}"
mkdir -p "${REPO_PATH}/${ARCH}"
echo "FILE_PATH=${FILE_PATH}"
env fpm -s dir -t rpm -a ${ARCH} -p ${FILE_PATH} -n ${PKG_NAME} -v ${PKG_VERSION} --iteration ${TODAY}.${ITER} \
    -m 'Christian Kniep <christian@qnib.org>' \
    --description 'pkg that encapsulates grok-patterns and provides a testing facility' \
    -C packaged/ etc usr
ec=$(echo $?)
echo "FPM EC: ${ec}"
if [ "X${ec}" != "X0" ];then
    exit ${ec}
fi
createrepo ${REPO_PATH}
