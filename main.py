from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def read_root():
    name = request.args.get('name')
    print(name)
    return jsonify(scrape_researchgate_profile(profile=name))

def scrape_researchgate_profile(profile: str):
    profile_data = {
        "basic_info": {},
        "about": {},
        "co_authors": [],
        "publications": [],
    }

    url = f"https://www.researchgate.net/profile/{profile}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    name_element = soup.select_one('.nova-legacy-e-text.nova-legacy-e-text--size-xxl')
    profile_data["basic_info"]["name"] = name_element.get_text(strip=True) if name_element else "Name not found"

    institution_element = soup.select_one('.nova-legacy-v-institution-item__stack-item a')
    profile_data["basic_info"]["institution"] = institution_element.get_text(strip=True) if institution_element else "Institution not found"

    department_element = soup.select_one('.nova-legacy-e-list__item.nova-legacy-v-institution-item__meta-data-item:nth-child(1)')
    profile_data["basic_info"]["department"] = department_element.get_text(strip=True) if department_element else "Department not found"

    current_position_element = soup.select_one('.nova-legacy-e-list__item.nova-legacy-v-institution-item__info-section-list-item')
    profile_data["basic_info"]["current_position"] = current_position_element.get_text(strip=True) if current_position_element else "Current position not found"

    lab_element = soup.select_one('.nova-legacy-o-stack__item .nova-legacy-e-link--theme-bare b')
    profile_data["basic_info"]["lab"] = lab_element.get_text(strip=True) if lab_element else "Lab not found"

    about_info = soup.select('.nova-legacy-c-card__body .nova-legacy-o-grid__column')
    profile_data["about"]["number_of_publications"] = about_info[0].get_text(strip=True) if about_info and len(about_info) > 0 else "Number of publications not found"
    profile_data["about"]["reads"] = about_info[1].get_text(strip=True) if about_info and len(about_info) > 1 else "Reads not found"
    profile_data["about"]["citations"] = about_info[2].get_text(strip=True) if about_info and len(about_info) > 2 else "Citations not found"
    profile_data["about"]["introduction"] = soup.select_one('.nova-legacy-o-stack__item .Linkify').get_text(strip=True) if soup.select_one('.nova-legacy-o-stack__item .Linkify') else "Introduction not found"
    profile_data["about"]["skills"] = [skill.get_text(strip=True) for skill in soup.select('.nova-legacy-l-flex__item .nova-legacy-e-badge')]

    for co_author in soup.select('.nova-legacy-c-card--spacing-xl .nova-legacy-c-card__body--spacing-inherit .nova-legacy-v-person-list-item'):
        profile_data["co_authors"].append({
            "name": co_author.select_one('.nova-legacy-v-person-list-item__align-content .nova-legacy-e-link').get_text(strip=True) if co_author.select_one('.nova-legacy-v-person-list-item__align-content .nova-legacy-e-link') else "Name not found",
            "link": co_author.select_one('.nova-legacy-l-flex__item a')['href'] if co_author.select_one('.nova-legacy-l-flex__item a') else "Link not found",
            "avatar": co_author.select_one('.nova-legacy-l-flex__item .lite-page-avatar img')['data-src'] if co_author.select_one('.nova-legacy-l-flex__item .lite-page-avatar img') else "Avatar not found",
            "current_institution": co_author.select_one('.nova-legacy-v-person-list-item__align-content li').get_text(strip=True) if co_author.select_one('.nova-legacy-v-person-list-item__align-content li') else "Current institution not found"
        })

    for publication in soup.select('#publications+ .nova-legacy-c-card--elevation-1-above .nova-legacy-o-stack__item'):
        profile_data["publications"].append({
            "title": publication.select_one('.nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare').get_text(strip=True) if publication.select_one('.nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare') else "Title not found",
            "date_published": publication.select_one('.nova-legacy-v-publication-item__meta-data-item span').get_text(strip=True) if publication.select_one('.nova-legacy-v-publication-item__meta-data-item span') else "Date published not found",
            "authors": [author.get_text(strip=True) for author in publication.select('.nova-legacy-v-person-inline-item__fullname')],
            "publication_type": publication.select_one('.nova-legacy-e-badge--theme-solid').get_text(strip=True) if publication.select_one('.nova-legacy-e-badge--theme-solid') else "Publication type not found",
            "description": publication.select_one('.nova-legacy-v-publication-item__description').get_text(strip=True) if publication.select_one('.nova-legacy-v-publication-item__description') else "Description not found",
            "publication_link": publication.select_one('.nova-legacy-c-button-group__item .nova-legacy-c-button')['href'] if publication.select_one('.nova-legacy-c-button-group__item .nova-legacy-c-button') else "Publication link not found",
        })

    return profile_data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

