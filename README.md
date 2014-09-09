# Breed (Git Continuous Deployment Framework)

## Breed allows you to deploy your git repositories continuously and intelligently.

- Processes a JSON payload
- Includes auth
- Includes per payload logging system
- Add your own operations
- Includes some standard operations (repo deployment, database deployment, see below)
- Simple test tools for debugging failed deployments

### Standard operations

- Database basic (i.e. Create or drop a database with the name of your repo_branch)
- Database copy (i.e. Create copy specifically for your feature branch from a master database)
- Database copy remote (i.e. Useful for copying the master database to a staging server)
- Database sql updates (i.e. Commit your sql changes and Breed updates your database automatically)
- Gitflow (Create unique urls for all feature, release and hotfix branches. Custom behaviour for dev, staging and prd environments. See more below)

### Requirements

- Breed is written in Python and tested on Centos, Python 2.6 running on WSGI
- Root access to your server
- Pip and easyinstall are needed to install modules.
- These python modules are required
    sudo pip install subprocess
    sudo easy_install web.py
    sudo pip install logging
    sudo pip install json
    sudo pip install os
    sudo pip install re
    sudo pip install base64
    
### Setup
- Make sure Python with WSGI is installed and modules mentioned above.
- Add Breed code in root folder of yourdomain.com
- Copy config_example.json to config.json
- Add your github token to config.json
- Change username and password in config.json
- Add your repo details to config.json
- Add your github.com hook : `http://username:password@yourdomain.com/deploy

### Troubleshooting

- Open http://yourdomain.com/deploy/test
- Here you can view and retry previous deployments
- You can see the payloads processed and the errors raised

## Gitflow Deployment

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

