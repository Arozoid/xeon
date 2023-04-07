import click
import json
import git
import requests
import requests_cache
from os import system as run
from os import path, listdir

@click.group()
def package_manager():
    pass

@package_manager.command()
@click.argument('package_name')
def install(package_name):
    click.echo(":: Syncronizing databases...")
    try:
        repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
    except git.exc.GitCommandError:
        run("rm -rf /tmp/xeondb")
        repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
    click.echo("database updated\n")
    click.echo("collecting data..")
    with open("/tmp/xeondb/packages.txt", "r") as f:
        for line in f:
            if package_name in line:
                data = requests.get(line.split()[2]).json()
                sdata = requests.get(line.split()[2]).text
                break
        else:
            click.echo(f"error: package '{package_name}' not found")
            exit()
    click.echo("checking for conflicts..")
    for conflict in data['conflicts']:
        if path.isfile(f"/tmp/xeondata/{conflict}.txt"):
            click.echo(f"error: {package_name} conflicts with {conflict}, exiting")
            exit()

    for depend in data['depends']:
        with open("/tmp/xeondb/packages.txt", "r") as f:
            for line in f:
                if depend in line:
                    ddata = requests.get(line.split()[2]).json()
                    break
        for conflict in ddata['conflicts']:
            if path.isfile(f"/tmp/xeondata/{conflict}.txt"):
                click.echo(f"error: dependency of {package_name} '{depend}' conflicts with {conflict}, exiting")
                exit()
    click.echo("resolving dependencies..\n")
    if data['depends'] == []:
        click.echo(f"Packages (1): {package_name}\n")
    else:
        click.echo(f"Packages ({len(data['depends']) + 1}): {package_name} {' '.join(map(str, data['depends']))}\n")
    if input("Proceed with installation? [Y/n] ") in ["y", "Y", ""]:
        click.echo(f':: Installing {package_name}...')
        if path.isfile(f"/tmp/xeondata/{package_name}.txt"):
            eval(data['uninstall'])
            eval(data['install'])
        else:
            eval(data['install'])
        click.echo("storing data..\n")
        if path.isdir("/tmp/xeondata"):
            if path.isfile(f"/tmp/xeondata/{package_name}.txt"):
                run(f"cd /tmp/xeondata && rm -rf {package_name}.txt && touch {package_name}.txt")
                with open(f"/tmp/xeondata/{package_name}.txt", "w") as f:
                        f.write(sdata)
            else:
                run(f"cd /tmp/xeondata && touch {package_name}.txt")
                with open(f"/tmp/xeondata/{package_name}.txt", "w") as f:
                        f.write(sdata)
        else:
            run(f"mkdir /tmp/xeondata && cd /tmp/xeondata && touch {package_name}.txt")
            with open(f"/tmp/xeondata/{package_name}.txt", "w") as f:
                        f.write(sdata)
        click.echo(":: Installing dependencies...")
        for depend in data['depends']:
            with open("/tmp/xeondb/packages.txt", "r") as f:
                for line in f:
                    if depend in line:
                        data = requests.get(line.split()[2]).json()
                        sdata = requests.get(line.split()[2]).text
                        break
                else:
                    click.echo(f"error: package '{depend}' not found")
                    exit()
            if path.isfile(f"/tmp/xeondata/{depend}.txt"):
                eval(data['uninstall'])
                eval(data['install'])
            else:
                eval(data['install'])
            click.echo("storing data..\n")
            if path.isdir("/tmp/xeondata"):
                if path.isfile(f"/tmp/xeondata/{depend}.txt"):
                    run(f'''cd /tmp/xeondata && rm -rf {depend}.txt && touch {depend}.txt''')
                    with open(f"/tmp/xeondata/{depend}.txt", "w") as f:
                        f.write(sdata)
                else:
                    run(f'''cd /tmp/xeondata && touch {depend}.txt''')
                    with open(f"/tmp/xeondata/{depend}.txt", "w") as f:
                        f.write(sdata)
            else:
                run(f'''mkdir /tmp/xeondata && cd /tmp/xeondata && touch {depend}.txt''')
                with open(f"/tmp/xeondata/{depend}.txt", "w") as f:
                        f.write(sdata)
            click.echo(f"installed '{depend}'")
        click.echo("finished all jobs, exiting xeon")
    else:
        click.echo("cancelled, exiting xeon")

@package_manager.command()
@click.argument('name')
@click.argument('link')
def add(name, link):
    if input(f"Proceed with the addition of '{name}' to the database? [Y/n] ") in ["y", "Y", ""]:
        pwd = input("Add a password (Secures uploaded packages from anyone updating package): ")
        try:
            repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
        except git.exc.GitCommandError:
            run("rm -rf /tmp/xeondb")
            repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
        click.echo(f':: Adding {name} to database...')
        run(f"echo '{pwd} {name} {link}' >> /tmp/xeondb/packages.txt")
        click.echo("added to local db")
        click.echo(":: Syncronizing database..")
        repo = git.Repo('/tmp/xeondb/')
        repo.index.add(["packages.txt"])
        repo.index.commit(f"added package {name} to db")
        click.echo("commited changes")

        origin = repo.remote(name="origin")
        origin.push()
        click.echo("pushed to cloud db")
        click.echo("finished all jobs, exiting xeon")

@package_manager.command()
@click.argument('name')
def remove(name):
    if input(f"Proceed with the removal of '{name}' from the database? [Y/n] ") in ["y", "Y", ""]:
        try:
            repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
        except git.exc.GitCommandError:
            run("rm -rf /tmp/xeondb")
            repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
        with open("/tmp/xeondb/packages.txt", "r") as f:
            for line in f:
                if name in line:
                    auth = line.split()[0]
                    rdata = line
                    break
            else:
                click.echo(f"error: package '{name}' not found")
                exit()

        with open("/tmp/xeondb/packages.txt", "r") as f:
            data = f.read()

        pwd = input("Enter the password for this package: ")
        if pwd == auth:
            click.echo(f':: Removing {name} from database...')
            with open("/tmp/xeondb/packages.txt", "w") as f:
                f.write(data.replace(rdata, ""))
            click.echo("removed from local db")
            click.echo(":: Syncronizing database..")
            repo = git.Repo('/tmp/xeondb/')
            repo.index.add(["packages.txt"])
            repo.index.commit(f"removed package {name} from db")
            click.echo("commited changes")

            origin = repo.remote(name="origin")
            origin.push()
            click.echo("pushed to cloud db")
            click.echo("finished all jobs, exiting xeon")
        else:
            click.echo("incorrect password, exiting xeon")
    else:
        click.echo("cancelled, exiting xeon")

@package_manager.command()
@click.argument('name')
@click.argument('link')
def update(name, link):
    if input(f"Proceed with the update of '{name}' in the database? [Y/n] ") in ["y", "Y", ""]:
        try:
            repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
        except git.exc.GitCommandError:
            run("rm -rf /tmp/xeondb")
            repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
        with open("/tmp/xeondb/packages.txt", "r") as f:
            for line in f:
                if name in line:
                    auth = line.split()[0]
                    oldlink = line.split()[2]
                    _line = line
                    break
            else:
                click.echo(f"error: package '{name}' not found")
                exit()

        with open("/tmp/xeondb/packages.txt", "r") as f:
            data = f.read()

        pwd = input("Enter the password for this package: ")
        if pwd == auth:
            click.echo(f':: Updating {name} in database...')
            with open("/tmp/xeondb/packages.txt", "w") as f:
                f.write(data.replace(_line, _line.replace(oldlink, link)))
            click.echo("added to local db")
            click.echo(":: Syncronizing database..")
            repo = git.Repo('/tmp/xeondb/')
            repo.index.add(["packages.txt"])
            repo.index.commit(f"updated package {name} in db")
            click.echo("commited changes")

            origin = repo.remote(name="origin")
            origin.push()
            click.echo("pushed to cloud db")
            click.echo("finished all jobs, exiting xeon")
        else:
            click.echo("incorrect password, exiting xeon")
    else:
        click.echo("cancelled, exiting xeon")

@package_manager.command()
@click.argument('query')
def search(query):
    description = []
    name = []
    click.echo(":: Syncronizing database..")
    try:
        repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
    except git.exc.GitCommandError:
        run("rm -rf /tmp/xeondb")
        repo = git.Repo.clone_from('https://Arozoid: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@github.com/Arozoid/xeonpkg.git', '/tmp/xeondb', branch='main')
    click.echo("database updated\n")
    with open("/tmp/xeondb/packages.txt", "r") as f:
        for line in f:
            if query in line.split()[1]:
                description.append(requests.get(line.split()[2]).json()['description'])
                name.append(line.split()[1])
                break
        else:
            click.echo(f"error: no queries were found")
            exit()

    for pkg, desc in zip(name, description):
        if path.isfile(f"/tmp/xeondata/{pkg}.txt"):  
            click.echo(f"xeon/{pkg} [installed]")
        else:
            click.echo(f"xeon/{pkg}")
        click.echo(f"{desc}\n")

@package_manager.command()
@click.argument('package_name')
def uninstall(package_name):
    if path.isfile(f"/tmp/xeondata/{package_name}.txt"):
        if input(f"Proceed with the uninstallation of '{package_name}'? [Y/n] ") in ["y", "Y", ""]:
            click.echo(f':: Removing {package_name}...')
            for file in listdir("/tmp/xeondata"):
                with open(f"/tmp/xeondata/{file}.txt", "r") as f:
                    data = f.read()

                if package_name in data["conflicts"]:
                    click.echo(f"error: {package_name} is a dependency of {file}")
            with open(f"/tmp/xeondata/{package_name}.txt", "r") as f:
                data = f.read()
            
            eval(json.loads(data)['uninstall'])
            click.echo("uninstalled package from system")
            run(f"rm -rf /tmp/xeondata/{package_name}.txt")
            click.echo("uninstalled memory of package")
            click.echo("finished all jobs, exiting xeon")
        else:
            print("cancelled, exiting xeon")
    else:
        print(f"error: the package '{package_name}' has not been installed yet")

if __name__ == '__main__':
    package_manager()