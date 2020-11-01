import os
import datetime

TEMP = "./temp/"
POSTS = "./posts/"
OUTPUT = "./feed/"

# TODO: Fix checking mtime if runtime becomes too long. Needs to check if templates has changed.

def to_variable(name, value):
    return '--variable ' + name + '=\'' + value + '\' '

def to_date_tuple(path):
    s = os.path.split(path)[0]
    day = os.path.split(path)[1]
    year = os.path.split(s)[0]
    month = os.path.split(s)[1]

    return (day, month, year)

def to_pretty_date(path):
    day, month, year = to_date_tuple(path)
    return datetime.datetime(int(year), int(month), int(day)).strftime('%b %d, %Y')

def to_month_tuple(path):
    year = os.path.split(path)[0]
    month = os.path.split(path)[1]

    return (month, year)

def to_pretty_month(path):
    month, year = to_month_tuple(path)
    return datetime.datetime(int(year), int(month), 1).strftime('%B, %Y')

months = []
days = []
entries = []

for year in os.listdir(POSTS):
    for month in os.listdir(os.path.join(POSTS, year)):
        months.append(os.path.join(year, month))
        for day in os.listdir(os.path.join(POSTS, year, month)):
            days.append(os.path.join(year, month, day))
            for entry in os.listdir(os.path.join(POSTS, year, month, day)):
                entries.append(os.path.join(year, month, day, os.path.splitext(entry)[0]))
            os.system('mkdir -p ' + os.path.join(TEMP, year, month, day))
            os.system('mkdir -p ' + os.path.join(OUTPUT, year, month, day))

months.sort()
days.sort()

for idx, entry in enumerate(entries):
    post_input = os.path.join(POSTS, entry + '.md')
    post_output = os.path.join(TEMP, entry + '.html')

    # if os.path.exists(post_output) and os.stat(post_output).st_mtime > os.stat(post_input).st_mtime:
    #     continue
    
    os.system('pandoc ' + post_input + ' --template templates/post.html -o ' + post_output)

for idx, day_path in enumerate(days):
    input_mtime = 0.0

    posts = []
    for post in os.listdir(os.path.join(TEMP, day_path)):
        path = os.path.join(TEMP, day_path, post)
        # post_time = os.stat(path).st_mtime
        # if post_time > input_mtime:
        #     input_mtime = post_time
        posts.append(path)
    
    day_output = os.path.join(OUTPUT, day_path, 'index.html')
    # if os.path.exists(day_output) and os.stat(day_output).st_mtime > input_mtime:
    #     continue

    day, month, year = to_date_tuple(day_path)

    variables = to_variable('date', to_pretty_date(day_path))

    if idx != 0:
        prev = days[idx-1]
        variables += to_variable('prev', prev)
        variables += to_variable('prev_text', to_pretty_date(prev))

    if idx != len(days) - 1:
        next = days[idx+1]
        variables += to_variable('next', next)
        variables += to_variable('next_text', to_pretty_date(next))
    
    os.system('pandoc ' + ' '.join(posts) + ' --template templates/day.html --metadata pagetitle="' + day_path + '" ' + variables + ' -o ' + day_output)

    output = os.path.join(TEMP, year, month, day + '.html')
    variables = to_variable('date', to_pretty_date(day_path))
    variables += to_variable('day_link', './' + day)
    os.system('pandoc ' + ' '.join(posts) + ' --template templates/day_of_month.html --metadata pagetitle="' + day_path + '" ' + variables + ' -o ' + output)

for idx, month_path in enumerate(months):
    input_mtime = 0.0

    posts = []
    with os.scandir(os.path.join(TEMP, month_path)) as it:
        for entry in it:
            if entry.is_file():
                # post_time = entry.stat().st_mtime
                # if post_time > input_mtime:
                #     input_mtime = post_time
                posts.append(os.path.join(TEMP, month_path, entry.name))

    output = os.path.join(OUTPUT, month_path, 'index.html')
    # if os.path.exists(output) and os.stat(output).st_mtime > input_mtime:
    #     continue

    posts.sort(reverse=True) # Most recent post first.

    variables = to_variable('date', to_pretty_month(month_path))

    if idx != 0:
        next = months[idx-1]
        variables += to_variable('next', next)
        variables += to_variable('next_text', to_pretty_month(next))

    if idx != len(months) - 1:
        prev = months[idx+1]
        variables += to_variable('prev', prev)
        variables += to_variable('prev_text', to_pretty_month(prev))

    os.system('pandoc ' + ' '.join(posts) + ' --template templates/month.html --metadata pagetitle="' + month_path + '" ' + variables + ' -o ' + output)

with open(os.path.join(OUTPUT, 'index.html'), 'w') as f:
    f.write('<meta http-equiv="refresh" content="0; URL=./'+ months[-1] +'" />\n')