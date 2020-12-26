#!/usr/bin/env python3
'''
Main CLI to rephile
'''
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

@cli.command("digest")
@click.option("-f", "--force", is_flag=True,
              help="Force an update to the cache")
@click.argument("files", nargs=-1)
@click.pass_context
def digest(ctx, force, files):
    digs = ctx.obj.digest(files, force)
    for dig in digs:
        click.echo(dig)
    

def main():
    cli(obj=None)

if '__main__' == __name__:
    main()
