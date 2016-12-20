# Udacity Simple Blog
https://udacity-blog-clyall.appspot.com/blog

## Description
This is a simple blog written mostly in Python for Google's App Engine. This project was performed for Udacity's [Intro to Backend](https://www.udacity.com/course/intro-to-backend--ud171) course.


## Getting Started
Please make sure you have the gcloud cli and Python 2.7 installed. Then using your command line change directory to enter the top most directory of the project, where the app.yaml file is located.

To start this project in a test environment run:
`dev_appserver.py .`

To start this project in production run:
`gcloud app deploy app.yaml index.yaml --project <project_name>`


## Usage
The purpose of this project is to illustrate how to build a simple blog in Google's App Engine using Python, Jinja2, and Google Datastore.


## Known Bugs
No known bugs at this time.


## Contributing
Chase Lyall, based on Steve Huffman's teachings from Udacity's [Intro to Backend](https://www.udacity.com/course/intro-to-backend--ud171) course.


## License
MIT License

Copyright (c) 2016 Chase Lyall

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.