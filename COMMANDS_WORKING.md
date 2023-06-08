# NICOLAS COMMAND WORKS FOR E2E TD.
export LLVM_BUILD_DIR=/scratch/general/vast/u1418973/temp/llvm-project/build/
export IREE_SAMPLES_DIR=/scratch/general/vast/u1418973/experiment/iree-samples/
export IREE_DIR=/scratch/general/vast/u1418973/experiment/iree-latest/


```
cat ${IREE_SAMPLES_DIR}/transform_dialect/examples/matmul.mlir |   sed "s/\${M}/3452/g" | sed "s/\${N}/1020/g" | sed "s/\${K}/2044/g" |   sed "s/private @fill_matmul_static(/@fill_matmul_static(/g" |   ${LLVM_BUILD_DIR}/bin/mlir-opt -symbol-dce |   ${IREE_DIR}/bin/iree-compile -     --iree-hal-target-backends=cuda --iree-hal-cuda-llvm-target-arch=sm_80 --iree-codegen-llvmgpu-enable-transform-dialect-matmul-tensorcore-strategy=true  --iree-hal-benchmark-dispatch-repeat-count=5  -o /tmp/foo.vmfb | ${IREE_DIR}/bin/iree-run-module --function=fill_matmul_static --device=cuda --module=/tmp/foo.vmfb --input=3452x2044xf32=1 --input=2044x1020xf32=1 --input=3452x1020xf32=1
```
