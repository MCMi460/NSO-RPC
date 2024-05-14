import os
import git


def get_version_info():
    r = git.repo.Repo(search_parent_directories=True)
    try:
        # Get all tags sorted by commit date
        tags = sorted(r.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
        version_info = tags[0].name
    except IndexError:
        try:
            version_info = r.active_branch.name
        except TypeError:
            version_info = r.head.object.hexsha[:7]
    return version_info


if __name__ == '__main__':
    if os.path.exists('version.txt'):
        os.remove('version.txt')

    version_info = get_version_info()
    with open('version.txt', 'w') as f:
        f.write(version_info)
