#
# SPDX-FileCopyrightText: Copyright (c) 1993-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numbers
from dataclasses import dataclass
from typing import Sequence, Set, Union

from mlir_tensorrt.compiler import ir
from mlir_tensorrt.compiler.dialects import stablehlo

from tripy import utils
from tripy.common.array import Array
from tripy.flat_ir.ops.base import BaseFlatIROp

import mlir_tensorrt.runtime.api as runtime


@dataclass(repr=False)
class ConstantOp(BaseFlatIROp):

    data: Union[Array, Sequence]

    def str_skip_fields(self) -> Set[str]:
        data_shape = self.data.shape if isinstance(self.data, Array) else self.outputs[0].shape
        if utils.should_omit_constant_in_str(data_shape):
            return {"data"}
        return set()

    def to_mlir(self, operands):
        import array
        import tripy.common.datatype as datatype
        from tripy.backend.mlir import utils as mlir_utils

        # TODO(#189): Remove explicit copy to host for constants
        if isinstance(self.data, Array):
            assert self.data.dtype == self.outputs[0].dtype
            memref_value = self.data.memref_value
            if self.data.device.kind == "gpu":
                memref_value = mlir_utils.MLIRRuntimeClient().copy_to_host(
                    device_memref=memref_value,
                    stream=None,
                )

            # Workaround (#208): bools are represented as i1 in MLIR-TRT but they cannot be used for DenseElementsAttr
            # so we have to represent them as ints and then cast the result
            if self.outputs[0].dtype == datatype.bool:
                # need to use memoryview.cast to ensure that the view will be flattened
                int_memref = self.data.runtime_client.create_memref(
                    array.array("i", memoryview(memref_value).cast("b").tolist()),
                    shape=self.data.shape,
                    dtype=mlir_utils.convert_tripy_dtype_to_runtime_dtype(datatype.int32),
                    device=None,
                )
                attr = ir.DenseElementsAttr.get(
                    array=int_memref, type=mlir_utils.get_mlir_dtype(datatype.int32), shape=self.data.shape
                )
                cast_output = mlir_utils.make_mlir_tensor(datatype.bool, self.data.shape)
                constant_op = stablehlo.ConstantOp(attr)
                return [stablehlo.ConvertOp(result=cast_output, operand=constant_op)]

            attr = ir.DenseElementsAttr.get(
                array=memref_value, type=mlir_utils.get_mlir_dtype(self.outputs[0].dtype), shape=self.data.shape
            )
        else:
            out_dtype = self.outputs[0].dtype

            def to_attrs(data):
                if isinstance(data, numbers.Number):
                    return [mlir_utils.get_mlir_scalar_attr(out_dtype, data)]
                attrs = []
                for element in data:
                    attrs.extend(to_attrs(element))
                return attrs

            attr = ir.DenseElementsAttr.get(attrs=to_attrs(self.data), type=self.outputs[0].to_mlir())

        return [stablehlo.ConstantOp(attr)]
