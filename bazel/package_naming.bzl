load("@rules_pkg//pkg:providers.bzl", "PackageVariablesInfo")

def _basic_naming_impl(ctx):
    val = {}
    val['target_cpu'] = ctx.attr.target_cpu
    val['target_os'] = ctx.attr.target_os
    return PackageVariablesInfo(values=val)

basic_naming = rule(
    implementation = _basic_naming_impl,
    attrs = {
        "target_cpu": attr.string(),
        "target_os": attr.string(),
    },
)
