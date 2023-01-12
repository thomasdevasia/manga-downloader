from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm
from PIL import Image


MANGA_LINK = 'https://read-vinlandsaga.com/'


# delete all files in download folder
def clear_download():
    for file in os.listdir('./download/'):
        os.remove('./download/' + file)


# read all images and merge pdf
def create_pdf(file_name, save_path='./final/', files_path='./download/'):
    images = []
    for img in sorted(os.listdir(files_path)):
        images.append(Image.open(files_path + img))
    images[0].save(save_path + file_name, save_all=True, append_images=images[1:])

# download the chapters
def download_chapter(chapter):

    name = chapter.a.text
    link = chapter.a['href']

    # getting the chapter content
    chapter_html = requests.get(link).text
    chapter_soup = BeautifulSoup(chapter_html, 'lxml')
    chapter_content = chapter_soup.find_all('div', class_='separator')
    
    for img in chapter_content:
        img_link = img.img['src']
        img_name = img_link.split('/')[-1]
        if int(img_name.split('.')[0]) < 10:
            img_name = '0' + img_name
        # download the image and save it
        image = requests.get(img_link).content
        with open(f'./download/{img_name}', 'wb') as f:
            f.write(image)

    create_pdf(name + '.pdf')
    clear_download()

def is_chapter_available(chapters, chapter_num):
    for chapter in chapters:
        if str(chapter_num) in chapter.text.split(':')[0]:
            return chapter
        
    return False

def main(link=MANGA_LINK):

    # Get the html text from the link
    html_txt = requests.get(link).text
    soup = BeautifulSoup(html_txt, 'lxml')

    # list of chapters links
    chapter_list = soup.find_all('ul', class_='su-posts')
    chapters = chapter_list[0].find_all('li', class_='su-post')[::-1]

    res = []

    print('Instructions:\n1. Use hyphen to download a range of chapters ex: 1-5\n2. Use comma to select specific chapters ex: 1,3,5\n3. Use -1 to download all chapters')
    
    num_chapters = input(f'How many chapters do you want to download?({len(chapters)} chapters available)):')

    if num_chapters == '-1':
        print('Downloading all chapters...')
        res = chapters
    # checking if contain both , and -
    elif ',' in num_chapters and '-' in num_chapters:
        print('Invalid input')
    # checking multiple hyphens
    elif num_chapters.count('-') > 1:
        print('Invalid input')
    elif ',' in num_chapters:
        print('Downloading selected chapters...')
        for i in num_chapters.split(','):
            res.append(is_chapter_available(chapters, i))
    elif '-' in num_chapters:
        print('Downloading range of chapters...')
        first, last = num_chapters.split('-')
        for i in range(int(first), int(last)+1):
            res.append(is_chapter_available(chapters, i))
    # checking if the input is a number
    elif num_chapters.isdigit():
        print('Downloading selected chapters...')
        res.append(is_chapter_available(chapters, num_chapters))
    else:
        print('Invalid input')

    pbar = tqdm(total=len(res))    
    for chapter in res:
        if chapter:
            tqdm.write(f'Downloading {chapter.a.text}...')
            download_chapter(chapter)
        pbar.update(1)

if __name__ == '__main__':

    # call the main download function
    main()