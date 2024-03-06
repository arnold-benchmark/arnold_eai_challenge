import os
import pandas as pd
import zipfile

def evaluate(test_annotation_file, user_annotation_file, phase_codename, **kwargs):
    
    df = pd.read_csv(test_annotation_file)
    folder_path = '/tmp/arnold_challenge'
    with zipfile.ZipFile(user_annotation_file, 'r') as zip_ref:
        if os.path.exists(folder_path):
            os.system(f'rm -r {folder_path}')
        zip_ref.extractall(folder_path)

    output_folder = folder_path

    metadata = {
        'file': [],
        'run': [],
        'success': [],
        'task': [],
        'split': []
    }
    # not_found = []
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            if file.endswith('.txt'):
                parts = root.split('/')
                
                entry = parts[-1]
                
                task = parts[-4]
                run = parts[-5].split('_')[2]
                # print(entry)
                # print('entry: ', entry)
                split = df[df['file'] == entry]['split']
                # if len(split.values) == 0:
                #     not_found.append(root)
                #     continue
                
                
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                    success = lines[0].strip() == 'success'
                metadata['file'].append(entry)
                metadata['run'].append(int(run))
                metadata['success'].append(success)
                metadata['task'].append(task)
                # print(split.values)
                metadata['split'].append(split.values[0])

    df2 = pd.DataFrame.from_dict(metadata)

    # Merge df and df2
    

    # For files in df not in df2, create three entries for each run with 'success' set to False
    missing_files = df[~df['file'].isin(df2['file'])]['file']
    # print(missing_files)
    # print(df)
    # exit()
    missing_entries = []
    for file in missing_files:
        for run in range(1, 4):  # Assuming runs are numbered 1, 2, 3
            missing_entries.append({ 'file': file, 'run': run, 'success': False,\
                                     'split': df[df['file'] == file]['split'].values[0], \
                                    'task': df[df['file'] == file]['task'].values[0]})
    
    # Append missing entries to df3
    df3 = pd.concat([df2, pd.DataFrame(missing_entries)], ignore_index=True)
    # Group by task, split, and run, then calculate the mean success rate
    grouped = df3.groupby(['task', 'split', 'run'])['success'].mean().reset_index()

    # Now, group by task and split, and calculate the mean of the success rates across runs
    final_grouped = grouped.groupby(['task', 'split'])['success'].mean().reset_index()

    output = {'result': []}

    for task in final_grouped['task'].unique():
        task_dict = {}
        task_data = final_grouped[final_grouped['task'] == task]

        for _, row in task_data.iterrows():
            task_dict[f"{row['split']}"] = {
                'SR': row['success']
            }

        output['result'].append({task: task_dict})
    overall_average = final_grouped['success'].mean()
    output['result'].append({'overall': overall_average})
    # print(output)
    return output

# evaluate('challenge_files_final.csv', '/home/nikepupu/Desktop/arnold/workspace/output.zip', '')
                