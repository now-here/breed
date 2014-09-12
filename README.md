# Breed

## Code in development - don't use yet.

## (Git Deploy Framework)

Breed allows you to deploy your git repositories continuously and intelligently.

- Processes a JSON payload
- Includes token auth on post-commit url
- Includes per payload logging system
- Add your own operations
- Includes some standard operations (repo deployment, database deployment, see below)
- Simple test tools for debugging failed deployments

### Standard operations

- Database copy (i.e. Create copy specifically for your feature branch from a master database)
- Gitflow (Create unique urls for all feature, release and hotfix branches. Custom behaviour for dev, staging and prd environments. See more below)
- Dir copy (i.e. Copy some files/dirs into the branch after it's deployed)

### Requirements

- Breed is written in Python and tested on Centos, Python 2.6 running on WSGI
- Root access to your server
- Pip and easyinstall are needed to install modules.
- Some python modules are required (see below)
    
### Setup
- Make sure Python with WSGI is installed.
- Install web.py `sudo easy_install web.py`
- Install some modules `sudo pip install -r reqirements.txt`
- Setup a url for breed (For example http://breed.yourdomain.com > pointing to /var/www/breed/run.py)
- @todo Example directives for Apache
- Copy config/general.ini.example to config/general.ini
- Change breed token, username and password
- Create logs folder in breed root (or elsewhere)
- Copy config/repo.ini.example to config/yourrepo_name.ini
- Set your deployment vars in config/yourrepo_name.ini
- Write your operations in operations/ @todo document how to write operations
- Add your github.com hook : `http://breed.yourdomain.com/deploy/breed_token


### Troubleshooting

- Open http://breed.yourdomain.com/deploy/test
- Here you can view and retry previous deployments
- You can see the payloads processed and the errors raised

## Rolled-in Operations


### Gitflow Deployment @todo - better written

Breed with gitflow deployment allows you to deploy each feature, release and hotfix branch on it's own unique url. Having a unique URL for each branch means that developers, designers, managers and clients can take a look at the URL to see the latest code in action. It also means that if you are working with Selenium testing on a service like testingbot.com or saucelabs.com – you can run all your tests on a single URL.

You create a feature, release or hotfix branch.

`git checkout develop`
`git branch feature-test`
`git push`

With GGD setup shortly after you push, the new branch will be available on a unique URL :

‘http://www.yourdomain.com/repo/feature-test OR`
‘http://feature-test-repo.yourdomain.com `

In a staging environment it will only setup release branches.
You can setup Breed on a production server to automatically deploy changes to the master branch - but be cautious!

