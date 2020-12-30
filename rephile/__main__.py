#!/usr/bin/env python3
'''
Main CLI to rephile
'''
import json
import click
import base64
import vignette

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
    # fixme: normalize the data better!
    from rephile.templates import render as doit
    from rephile.digest import asdict
    digs = ctx.obj.digest(files, force)
    byhash = dict()
    bypath = dict()
    for f,d in zip(files,digs):
        bh = asdict(d)
        bh['path'] = f
        thumbpath = vignette.get_thumbnail(f)
        thumbdata = base64.b64encode(open(thumbpath,'rb').read()).decode()
        bh['thumb'] = dict(path=thumbpath, data=thumbdata)
        byhash[d.sha256] = bh
        bypath[f] = d

    # Model provides top level keys used by template
    model = dict(byhash=byhash, bypath=bypath)
    text = doit(template, model)
    print (text)
    

@cli.command("make")
@click.option("-n", "--dry-run", is_flag=True,
              help="Do or do not, there is no try.  Except using this flag")
@click.option("-m", "--method", default="copy",
              type=click.Choice(["copy","move","hard","link"]),
              help="Method for making a file from input files")
@click.argument("files", nargs=-1)
@click.pass_context
def make(ctx, files):
    'Make a file in some way'


def main():
    cli(obj=None)

if '__main__' == __name__:
    main()
