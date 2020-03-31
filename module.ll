; ModuleID = "module.bc"
target triple = "i686-pc-windows-msvc"
target datalayout = "e-m:e-p:32:32-i64:64-f80:32-n8:16:32-a:0:32-S32"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

define i32 @"main"() 
{
entry:
  %"x" = alloca i32, align 4
  %"y" = alloca float, align 4
  store i32 0, i32* %"x"
  store float              0x0, float* %"y"
  %".4" = call i32 @"leiaInteiro"()
  store i32 %".4", i32* %"x"
  %".6" = call float @"leiaFlutuante"()
  store float %".6", float* %"y"
  %"write_var" = load i32, i32* %"x", align 4
  call void @"escrevaInteiro"(i32 %"write_var")
  %"write_var.1" = load float, float* %"y", align 4
  call void @"escrevaFlutuante"(float %"write_var.1")
  ret i32 0
}
