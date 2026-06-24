"""Reusable fastverk tectonic-doc tooling.

`brand_doc` compiles a `.tex` into a PDF with the `fastverk` LaTeX class + brand
fonts auto-staged — a consuming doc only writes `\\documentclass{fastverk}` and
references figures at their workspace-relative paths. The resource bundle (class
+ fonts) is carried by `BrandResourcesInfo`, so other repos can depend on
`@brand//doc:resources` and get the same styling.
"""

BrandResourcesInfo = provider(
    doc = "Class + font resources auto-staged into every fastverk tectonic doc.",
    fields = {"files": "depset of resource Files (.cls/.sty staged at cwd; fonts at fonts/)"},
)

def _brand_resources_impl(ctx):
    return [BrandResourcesInfo(files = depset(ctx.files.srcs))]

brand_resources = rule(
    implementation = _brand_resources_impl,
    attrs = {"srcs": attr.label_list(allow_files = True, mandatory = True)},
    doc = "Bundle the fastverk class + fonts into a BrandResourcesInfo.",
)

def _brand_doc_impl(ctx):
    info = ctx.toolchains["@rules_tectonic//tectonic:toolchain_type"].tectonicinfo
    out = ctx.actions.declare_file(ctx.label.name + ".pdf")
    res = ctx.attr.resources[BrandResourcesInfo].files.to_list()
    doc_inputs = [ctx.file.main] + ctx.files.srcs
    main_sp = ctx.file.main.short_path
    maindir = main_sp.rsplit("/", 1)[0] if "/" in main_sp else "."
    base = ctx.file.main.basename.rsplit(".", 1)[0]

    # Stage at workspace-relative paths (figures resolve as the .tex references
    # them, e.g. ../icons/x.png), then cd into the main's dir and run tectonic —
    # which resolves includes relative to that dir. Class/style + fonts are
    # staged INTO the main's dir (the class at cwd; fonts under fonts/) so
    # \documentclass{fastverk} and Path=fonts/ resolve with no author wiring.
    stage = [(f.path, f.short_path) for f in doc_inputs]
    for f in res:
        dst = "%s/%s" % (maindir, f.basename) if f.extension in ("cls", "sty") else "%s/fonts/%s" % (maindir, f.basename)
        stage.append((f.path, dst))

    lines = ["set -e", "STAGE=$(mktemp -d)", "EXEC=$(pwd)"]
    seen = {}
    for src, dst in stage:
        d = dst.rsplit("/", 1)[0] if "/" in dst else "."
        if d not in seen:
            lines.append('mkdir -p "$STAGE/%s"' % d)
            seen[d] = True
        lines.append('cp -L "$EXEC/%s" "$STAGE/%s"' % (src, dst))

    lines += [
        'TECTONIC="$EXEC/%s"' % info.tectonic.path,
        'cd "$STAGE/%s"' % maindir,
        '"$TECTONIC" -X compile --outdir . --keep-logs "%s"' % ctx.file.main.basename,
        'mv "%s.pdf" "$EXEC/%s"' % (base, out.path),
    ]
    ctx.actions.run_shell(
        command = "\n".join(lines),
        tools = [info.tectonic],
        inputs = doc_inputs + res,
        outputs = [out],
        mnemonic = "BrandDoc",
        progress_message = "Compiling brand doc %{label}",
        use_default_shell_env = True,
    )
    return [DefaultInfo(files = depset([out]))]

brand_doc = rule(
    implementation = _brand_doc_impl,
    attrs = {
        "main": attr.label(
            allow_single_file = [".tex"],
            mandatory = True,
            doc = "Top-level .tex; should use \\documentclass{fastverk}.",
        ),
        "srcs": attr.label_list(
            allow_files = True,
            doc = "Figures + extra inputs, referenced at workspace-relative paths.",
        ),
        "resources": attr.label(
            providers = [BrandResourcesInfo],
            default = "//doc:resources",
            doc = "The fastverk class + fonts bundle.",
        ),
    },
    toolchains = ["@rules_tectonic//tectonic:toolchain_type"],
    doc = "Compile a .tex into a PDF with the fastverk class + fonts auto-bundled.",
)
