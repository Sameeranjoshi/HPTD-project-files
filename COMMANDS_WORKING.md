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

# IREE TD tensor-core strategy file which works in IREE is now migrated to HPTD with removing fill from it.
This works with HPTD as it is, no fill required, and it fails with iree-compile.

```
transform.sequence failures(propagate) {
^bb1(%variant_op: !transform.any_op):
%0 = transform.structured.match ops{["linalg.matmul"]} in %variant_op : (!transform.any_op) -> !transform.any_op
%1, %2 = transform.structured.tile_to_forall_op %0 tile_sizes [128, 128] { mapping = [#gpu.block<y>,#gpu.block<x>] }: (!transform.any_op) -> (!transform.any_op, !transform.any_op)
transform.iree.populate_workgroup_count_region_using_num_threads_slice %1 : (!transform.any_op) -> ()
%3 = transform.structured.match ops{["linalg.matmul"]} in %variant_op : (!transform.any_op) -> !transform.any_op
%4, %5 = transform.structured.tile %3 [0, 0, 16] : (!transform.any_op) -> (!transform.any_op, !transform.any_op)
%6 = transform.structured.pad %4 { padding_values = [0.00000 : f32, 0.00000 : f32, 0.00000 : f32], padding_dimensions = [0, 1, 2], pack_paddings=[1, 1, 1]} : (!transform.any_op) -> !transform.any_op
%7 = transform.get_producer_of_operand %6[2] : (!transform.any_op) -> !transform.any_op
%8 = transform.cast %7 : !transform.any_op to !transform.op<"tensor.pad">
%9 =  transform.structured.hoist_pad %8 by 1 loops : (!transform.op<"tensor.pad">) -> !transform.any_op
%10 = transform.structured.match ops{["tensor.parallel_insert_slice"]} in %variant_op : (!transform.any_op) -> !transform.any_op
%11 = transform.structured.insert_slice_to_copy %10 : (!transform.any_op) -> !transform.any_op
transform.iree.apply_patterns %variant_op { canonicalization, cse, licm, tiling_canonicalization } : (!transform.any_op) -> ()
%12 = transform.get_producer_of_operand %6[0] : (!transform.any_op) -> !transform.any_op
%13, %14 = transform.structured.tile_to_forall_op %12 num_threads [16, 8] tile_sizes []{ mapping = [#gpu.linear<x>,#gpu.linear<y>] }: (!transform.any_op) -> (!transform.any_op, !transform.any_op)
%15 = transform.structured.match ops{["scf.if"]} in %13 : (!transform.any_op) -> !transform.any_op
transform.scf.take_assumed_branch %15 take_else_branch : (!transform.any_op) -> ()
%16 = transform.get_producer_of_operand %6[1] : (!transform.any_op) -> !transform.any_op
%17, %18 = transform.structured.tile_to_forall_op %16 num_threads [2, 64] { mapping = [#gpu.linear<y>,#gpu.linear<x>] }: (!transform.any_op) -> (!transform.any_op, !transform.any_op)
%19 = transform.structured.match ops{["scf.if"]} in %17 : (!transform.any_op) -> !transform.any_op
transform.scf.take_assumed_branch %19 take_else_branch : (!transform.any_op) -> ()
%20, %21 = transform.structured.tile_to_forall_op %11 num_threads [2, 64] { mapping = [#gpu.linear<y>,#gpu.linear<x>] }: (!transform.any_op) -> (!transform.any_op, !transform.any_op)
transform.iree.apply_patterns %variant_op { canonicalization, cse, licm, tiling_canonicalization } : (!transform.any_op) -> ()
transform.structured.masked_vectorize %14 vector_sizes [8, 2] : !transform.any_op
transform.structured.masked_vectorize %18 vector_sizes [8, 2] : !transform.any_op
transform.structured.masked_vectorize %21 vector_sizes [64, 2] : !transform.any_op
%22 = transform.structured.match ops{["func.func"]} in %variant_op : (!transform.any_op) -> !transform.any_op
%23 = transform.vector.lower_masked_transfers %22 : (!transform.any_op) -> !transform.any_op
%24 = transform.structured.match ops{["linalg.matmul"]} in %variant_op : (!transform.any_op) -> !transform.any_op
%25, %26 = transform.structured.tile_to_forall_op %24 num_threads [2, 64] { mapping = [#gpu.thread<y>,#gpu.thread<x>] }: (!transform.any_op) -> (!transform.any_op, !transform.any_op)
%27 = transform.structured.match ops{["linalg.matmul"]} in %variant_op : (!transform.any_op) -> !transform.any_op
%28 = transform.structured.match ops{["func.func"]} in %variant_op : (!transform.any_op) -> !transform.any_op
transform.iree.apply_patterns %28 { rank_reducing_linalg, rank_reducing_vector } : (!transform.any_op) -> ()
%29 = transform.structured.vectorize %28 : (!transform.any_op) -> !transform.any_op
transform.iree.apply_patterns %variant_op { canonicalization, cse, licm, tiling_canonicalization } : (!transform.any_op) -> ()
%31 = transform.structured.match ops{["func.func"]} in %variant_op : (!transform.any_op) -> !transform.any_op
transform.structured.hoist_redundant_tensor_subsets %31 : (!transform.any_op) -> ()
transform.iree.apply_patterns %variant_op { canonicalization, cse, licm, tiling_canonicalization } : (!transform.any_op) -> ()
%30 = transform.iree.bufferize { target_gpu } %variant_op : (!transform.any_op) -> (!transform.any_op)
%32 = transform.structured.match ops{["func.func"]} in %30 : (!transform.any_op) -> !transform.any_op
transform.iree.erase_hal_descriptor_type_from_memref %32 : (!transform.any_op) -> ()
transform.iree.apply_buffer_optimizations %32 : (!transform.any_op) -> ()
%33 = transform.structured.match ops{["func.func"]} in %30 : (!transform.any_op) -> !transform.any_op
transform.iree.apply_patterns %33 {canonicalization, cse, licm, tiling_canonicalization} : (!transform.any_op) -> ()
transform.iree.forall_to_workgroup %33 : (!transform.any_op) -> ()
%34 = transform.structured.match ops{["func.func"]} in %30 : (!transform.any_op) -> !transform.any_op
transform.iree.map_nested_forall_to_gpu_threads %34 workgroup_dims = [64, 2, 1] : (!transform.any_op) -> ()
%35 = transform.structured.match ops{["func.func"]} in %30 : (!transform.any_op) -> !transform.any_op
%36 = transform.vector.lower_masks %35 : (!transform.any_op) -> !transform.any_op
%37 = transform.vector.materialize_masks %36 : (!transform.any_op) -> !transform.any_op
transform.iree.apply_patterns %30 {fold_memref_aliases, canonicalization, cse, licm, tiling_canonicalization} : (!transform.any_op) -> ()
%38 = transform.structured.match ops{["func.func"]} in %30 : (!transform.any_op) -> !transform.any_op
transform.iree.hoist_static_alloc %38 : (!transform.any_op) -> ()
}
```
