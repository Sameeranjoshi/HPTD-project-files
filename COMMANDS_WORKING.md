# NICOLAS COMMAND WORKS FOR E2E TD.
```
export LLVM_BUILD_DIR=/scratch/general/vast/u1418973/temp/llvm-project/build/
export IREE_SAMPLES_DIR=/scratch/general/vast/u1418973/experiment/iree-samples/
export IREE_DIR=/scratch/general/vast/u1418973/experiment/iree-latest/
```

```
cat ${IREE_SAMPLES_DIR}/transform_dialect/examples/matmul.mlir |   sed "s/\${M}/510/g" | sed "s/\${N}/510/g" | sed "s/\${K}/510/g" |   sed "s/private @fill_matmul_static(/@fill_matmul_static(/g" |   ${LLVM_BUILD_DIR}/bin/mlir-opt -symbol-dce |   ${IREE_DIR}/bin/iree-compile -     --iree-hal-target-backends=cuda --iree-hal-cuda-llvm-target-arch=sm_80 --iree-codegen-llvmgpu-enable-transform-dialect-matmul-tensorcore-strategy=true  --iree-hal-benchmark-dispatch-repeat-count=5  -o /tmp/foo.vmfb && ${IREE_DIR}/bin/iree-run-module --function=fill_matmul_static --device=cuda --module=/tmp/foo.vmfb --input=510x510xf32=1 --input=510x510xf32=1 --input=510x510xf32=1
```


# To see the TD IR generated from tensor-core strategy, which they use TransformDialectStrategies/

```
cat ${IREE_SAMPLES_DIR}/transform_dialect/examples/matmul.mlir |   sed "s/\${M}/510/g" | sed "s/\${N}/510/g" | sed "s/\${K}/510/g" |   sed "s/private @fill_matmul_static(/@fill_matmul_static(/g" |   ${LLVM_BUILD_DIR}/bin/mlir-opt -symbol-dce |   ${IREE_DIR}/bin/iree-opt      --iree-hal-target-backends=cuda    --iree-hal-cuda-llvm-target-arch=sm_80  --iree-abi-transformation-pipeline      --iree-flow-transformation-pipeline      --iree-stream-transformation-pipeline      --iree-hal-configuration-pipeline | ${IREE_DIR}/bin/iree-opt  --pass-pipeline="builtin.module(hal.executable(hal.executable.variant(iree-llvmgpu-lower-executable-target{test-lowering-configuration})))" --iree-codegen-llvmgpu-enable-transform-dialect-matmul-tensorcore-strategy --iree-codegen-llvmgpu-enable-transform-dialect-aligned-matmul
```
This will generate the TD automatically 

# Want to see the output after applying the TD strategy which is automatically generated from above flag ? Remove the `test-lowering-configuration` flag.
```
cat ${IREE_SAMPLES_DIR}/transform_dialect/examples/matmul.mlir |   sed "s/\${M}/510/g" | sed "s/\${N}/510/g" | sed "s/\${K}/510/g" |   sed "s/private @fill_matmul_static(/@fill_matmul_static(/g" |   ${LLVM_BUILD_DIR}/bin/mlir-opt -symbol-dce |   ${IREE_DIR}/bin/iree-opt      --iree-hal-target-backends=cuda    --iree-hal-cuda-llvm-target-arch=sm_80  --iree-abi-transformation-pipeline      --iree-flow-transformation-pipeline      --iree-stream-transformation-pipeline      --iree-hal-configuration-pipeline | ${IREE_DIR}/bin/iree-opt  --pass-pipeline="builtin.module(hal.executable(hal.executable.variant(iree-llvmgpu-lower-executable-target)))" --iree-codegen-llvmgpu-enable-transform-dialect-matmul-tensorcore-strategy --iree-codegen-llvmgpu-enable-transform-dialect-aligned-matmul
```
