import pytest
import requests
from pydantic import BaseModel, ValidationError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

class ArtObject(BaseModel):
    objectID: int
    isHighlight: bool
    accessionNumber: str
    accessionYear: str
    isPublicDomain: bool
    primaryImage: str
    artistDisplayName: str
    title: str
    objectDate: str
    medium: str
    dimensions: str

class SearchResult(BaseModel):
    total: int
    objectIDs: list[int]

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

@pytest.mark.parametrize("object_id", [436121, 437329, 436524])
def test_get_art_object_by_id(object_id):
    url = f"{BASE_URL}/objects/{object_id}"
    response = requests.get(url)
    
    logger.info(f"Запрос: {url}")
    logger.info(f"Ответ: {response.status_code}, {response.json()}")

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        art_object = ArtObject(**response.json())
        logger.info("Валидация структуры данных успешна")
    except ValidationError as e:
        logger.error(f"Ошибка валидации: {e}")
        pytest.fail(f"Валидация провалена: {e}")

def test_get_art_object_with_invalid_id():
    invalid_id = 999999999  # Несуществующий идентификатор
    url = f"{BASE_URL}/objects/{invalid_id}"
    response = requests.get(url)
    
    logger.info(f"Запрос: {url}")
    logger.info(f"Ответ: {response.status_code}, {response.json()}")
    
    # Ожидаем 404 ошибку для несуществующего объекта
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"

def test_search_art_objects():
    query = "sunflowers"
    url = f"{BASE_URL}/search?q={query}"
    response = requests.get(url)
    
    logger.info(f"Запрос: {url}")
    logger.info(f"Ответ: {response.status_code}, {response.json()}")

    # Проверка статуса ответа
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        search_result = SearchResult(**response.json())
        logger.info("Валидация структуры данных поиска успешна")
        assert search_result.total > 0, "Результаты поиска должны возвращать хотя бы один объект"
    except ValidationError as e:
        logger.error(f"Ошибка валидации: {e}")
        pytest.fail(f"Валидация провалена: {e}")

def test_search_limit_results():
    query = "cat"
    url = f"{BASE_URL}/search?q={query}&departmentId=6"
    response = requests.get(url)
    
    logger.info(f"Запрос: {url}")
    logger.info(f"Ответ: {response.status_code}, {response.json()}")
    
    # Проверка статуса ответа
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    search_result = response.json()
    assert len(search_result['objectIDs']) <= 100, "Количество возвращаемых результатов должно быть ограничено 100"

def test_search_with_filter():
    query = "quilt"
    medium = "Silk"
    url = f"{BASE_URL}/search?q={query}&medium={medium}"
    response = requests.get(url)
    
    logger.info(f"Запрос: {url}")
    logger.info(f"Ответ: {response.status_code}, {response.json()}")
    
    # Проверка статуса ответа
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    search_result = response.json()
    assert search_result['total'] > 0, "Ожидается хотя бы один результат"
    assert all(isinstance(obj_id, int) for obj_id in search_result['objectIDs']), "Все ID объектов должны быть целыми числами"
