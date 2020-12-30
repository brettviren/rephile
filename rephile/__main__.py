#!/usr/bin/env python3
'''
Main CLI to rephile
'''
import os
import shutil
import json
import click

from rephile import Rephile
from rephile.jobs import pmapgroup
import rephile.db as rdb


@click.group()
@click.option("-c", "--cache",
              type=click.Path(dir_okay=False, file_okay=True,
                              resolve_path=True),
              envvar='REPHILE_CACHE',
              default=None,
              help="The rephile cache")
@click.option("-j","--jobs",default=1,
              help="Number of concurrent jobs may be run")
@click.pass_context
def cli(ctx, cache, jobs):
    '''
    rephile refiles your files
    '''
    ctx.obj = Rephile(cache, jobs)


@cli.command("exif")
@click.argument("files", nargs=-1)
@click.pass_context
def exif(ctx, files):
    'Print EXIF as JSON'
    dat = ctx.obj.exif(files)
    click.echo(json.dumps(dat, indent=4))


@cli.command("hashsize")
@click.argument("files", nargs=-1)
@click.pass_context
def hashsize(ctx, files):
    'Print hash and size of files'
    hs = ctx.obj.hashsize(files)
    for p, (h, s) in zip(files, hs):
        click.echo(f"{s:10} {h} {p}")


@cli.command("init")
@click.pass_context
def init(ctx):
    'Initialize a rephile cache database'
    ctx.obj.init()

@cli.command("digest")
@click.option("-F", "--force", is_flag=True,
              help="Force an update to the cache")
@click.argument("files", nargs=-1)
@click.pass_context
def digest(ctx, force, files):
    'Import information about files'
    digs = ctx.obj.digest(files, force)
    for dig in digs:
        click.echo(dig)
    

@cli.command("lines")
@click.option("-F", "--force", is_flag=True,
              help="Force an update to the cache")
@click.option("-f", "--format", default="{SourceFile}",
              help="F-string to apply to file metadata")
@click.option("-d", "--delimiter", default="\n",
              help="Delimiter of lines of text")
@click.argument("files", nargs=-1)
@click.pass_context
def lines(ctx, force, format, delimiter, files):
    'Format information about each file into one line of text.'
    from rephile.digest import astext
    digs = ctx.obj.digest(files, force)
    lines = list()
    for dig in digs:
        lines.append(astext(dig, format))
    text = delimiter.join(lines)
    #click.echo(text)
    print (text.encode("latin1").decode('unicode-escape'))


@cli.command("render")
@click.option("-F", "--force", is_flag=True,
              help="Force an update to the cache")
@click.option("-t", "--template", type=click.Path(),
              help="A template file to render")
@click.argument("files", nargs=-1)
@click.pass_context
def render(ctx, force, template, files):
    'Render template against model'

    # model consists of
    # digs: map from hash to Digest object
    # paths: map from file system path to hash
    
    # fixme: factor this into rephile.main and further.

    from rephile.templates import render as doit
    digs_inorder = ctx.obj.digest(files, force)
    digs = dict()
    paths = dict()
    for path, dig in zip(files, digs_inorder):
        digs[dig.id] = dig
        paths[path] = dig.id

    # Model provides top level keys used by template
    model = dict(digs=digs, paths=paths)
    text = doit(template, model)
    print (text)
    

@cli.command("make")
@click.option("-n", "--dry-run", is_flag=True,
              help="Do or do not, there is no try.  Except using this flag")
@click.option("-F", "--force", is_flag=True,
              help="Force an update to the cache")
@click.option("-f", "--format", default="{SourceFile}",
              help="F-string to apply to file metadata")
@click.option("-m", "--method", default="copy",
              type=click.Choice(["copy","move","hard","soft",]),
              help="Method for making a file from input files")
@click.argument("files", nargs=-1)
@click.pass_context
def make(ctx, dry_run, force, format, method, files):
    'Make new files from old'
    from rephile.digest import astext

    digs = ctx.obj.digest(files, force)

    new_paths = list()
    for dig in digs:
        new_paths.append(astext(dig, format))

    for src, tgt, dig in zip(files, new_paths, digs):
        if os.path.abspath(src) == os.path.abspath(tgt):
            print(f"same: {src} <--> {tgt}")
            return

        print(f"{method}: {src} ---> {tgt}")
        if dry_run:
            continue

        tgt_dir = os.path.dirname(tgt)
        if not os.path.exists(tgt_dir):
            os.makedirs(tgt_dir)

        if os.path.exists(tgt):
            os.remove(src)

        if method == "copy":
            shutil.copy(src, tgt, follow_symlinks=False)
            continue

        if method == "move":
            shutil.move(src, tgt)
            continue

        if method == "soft":
            if os.path.islink(src):
                os.symlink(os.path.realpath(src), tgt)
            else:
                os.symlink(src, tgt)
            continue
    
        if method == "hard":
            os.link(src, tgt)
            continue




@cli.command("asdata")
@click.argument("files", nargs=-1)
@click.pass_context
def asdata(ctx, files):
    'File info as avilable to format'
    from rephile.paths import asdict
    paths = ctx.obj.paths(files)
    text = json.dumps([asdict(p) for p in paths], indent=4)
    print(text)
    

def main():
    cli(obj=None)

if '__main__' == __name__:
    main()
