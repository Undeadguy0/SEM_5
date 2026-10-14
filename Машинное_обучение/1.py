# !pip install nbformat -q
import nbformat as nbf

cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

# ============================================================
# 1. Титул и импорты
# ============================================================

md("""# Практическое занятие №3-4

**Дисциплина:** Алгоритмы машинного обучения для решения прикладных задач  
**Тема:** Парная линейная регрессия, полиномиальная регрессия.  
Гребневая регрессия, LASSO, Elastic Net.  
**МИРЭА — Российский технологический университет**  
Доцент кафедры индустриального программирования, к.ф.-м.н. Осипов Алексей Викторович  
Москва, 2026 г.
""")

code("""# Импорт библиотек
try:
    import google.colab
    IN_COLAB = True
except:
    IN_COLAB = False

if IN_COLAB:
    # Если нужен requirements.txt, раскомментируйте и укажите ссылку:
    # !wget -q -O requirements.txt <URL>
    # !pip install -q -r requirements.txt
    pass

from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Настройки отображения
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (8, 5)
""")

# ============================================================
# 2. Iris
# ============================================================

md("""## Ирисы Фишера

Выборка взята отсюда:  
https://archive.ics.uci.edu/ml/datasets/iris
""")

md("""### Загрузка выборки""")

code("""# Загружаем датасет Iris
# Последний столбец — класс.
dataset = pd.read_csv(
    'https://raw.githubusercontent.com/andriygrav/MachineLearningSeminars/master/sem1/data/iris.data',
    header=None,
    names=[
        'длина чашелистика',
        'ширина чашелистика',
        'длина лепестка',
        'ширина лепестка',
        'klacc'
    ]
)

# Смотрим несколько случайных строк
dataset.sample(5, random_state=0)
""")

md("""### Начало работы с данными

1. Определить множество объектов:
   - размер выборки;
   - признаки, которыми описываются объекты.
2. Определить множество ответов.
3. Определить тип задачи машинного обучения.
""")

code("""# Размер выборки
print('Размер выборки составляет l={} объектов.'.format(len(dataset)))

# Признаки
print('Признаки:', list(dataset.columns[:-1]))

# Классы
print('Классы:', dataset['klacc'].unique())
""")

md("""### Анализ данных

Проектируем объекты на двумерные плоскости для упрощения анализа.
""")

code("""# Визуализация попарных зависимостей
# hue — цвет по классу
sns.pairplot(dataset, hue='klacc', height=2)
plt.show()
""")

md("""Из рисунка видно, что класс `Iris-setosa` легко отделяется от двух других.  
`Iris-versicolor` и `Iris-virginica` разделяются сложнее, но всё же можно провести прямую, которая их разделит.
""")

# ============================================================
# 3. Бинарная классификация Iris
# ============================================================

md("""## Построение модели

### Преобразование данных

Исходная задача — классификация на 3 класса.  
Для наглядности рассмотрим бинарную классификацию: удалим объекты класса `Iris-setosa`.
""")

code("""# Удаляем Iris-setosa
binary_dataset = dataset.drop(index=dataset.index[dataset['klacc'] == 'Iris-setosa']).copy()

# Кодируем классы числами: Iris-versicolor -> -1, Iris-virginica -> 1
binary_dataset.loc[binary_dataset['klacc'] == 'Iris-versicolor', 'klacc'] = -1
binary_dataset.loc[binary_dataset['klacc'] == 'Iris-virginica', 'klacc'] = 1

# Проверяем
binary_dataset['klacc'].value_counts()
""")

md("""### Модель алгоритмов

Семейство линейных классификаторов:

\[
\\mathfrak{F}_{bcl} = \\{ f(\\theta, x) = \\text{sign}(\\theta^T x) \\mid \\theta \\in \\mathbb{R}^n \\}.
\]

### Функция потерь

Эмпирический риск:

\[
L(f, X, y) = \\sum_{i=1}^{l} q(f, x_i, y_i).
\]

Оптимизационная задача:

\[
\\hat{f} = \\arg \\min_{f \\in \\mathfrak{F}} L(f, X, y).
\]

Для бинарной классификации:

\[
L(\\theta, X, y) = \\sum_{i=1}^{l} [f(\\theta, x_i) \\neq y_i].
\]
""")

md("""### Поиск оптимального вектора параметров

Переходим к матрице объектов \(X \\in \\mathbb{R}^{l \\times (n+1)}\) и вектору ответов \(y \\in \\{-1, 1\\}^l\).  
Добавляем столбец единиц для свободного члена.
""")

code("""# Формируем матрицу признаков и вектор ответов
X = binary_dataset.drop(columns='klacc').values
y = binary_dataset['klacc'].values.reshape(-1)

# Добавляем столбец единиц ( bias / свободный член )
X = np.hstack([X, np.ones([len(X), 1])]).astype(np.float64)
y = y.astype(np.int64)

# Обучаем логистическую регрессию
model = LogisticRegression(random_state=0, max_iter=2000)
model.fit(X, y)

# Вектор оптимальных параметров
print('Коэффициенты модели:')
print(model.coef_)
""")

# ============================================================
# 4. Практическая часть: winequality-red
# ============================================================

md("""## Практическая часть: классификация вина

Загрузите файл `winequality-red.csv` с помощью `pd.read_csv`.  
Последний столбец отвечает за качество вина.  
Будем считать, что **хорошее вино** — это качество **7 и выше**.  
Остальное вино — **некачественное**.

Нужно сделать классификацию вина по данному датасету.  
Два класса: `"Хорошее"` и `"Не качественное"`.  
Результатом будем считать уравнение гиперповерхности, отделяющее один класс от другого.
""")

md("""### Загрузка и подготовка данных""")

code("""# Загружаем датасет red wine quality.
# UCI-файл разделён точкой с запятой, поэтому sep=';'
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"

try:
    wine = pd.read_csv(url, sep=';')
except Exception as e:
    print("Не удалось скачать по URL, пробую локальный файл winequality-red.csv")
    wine = pd.read_csv('winequality-red.csv', sep=';')

# Последний столбец quality. Хорошее вино — quality >= 7.
wine['good'] = (wine['quality'] >= 7).astype(int)

# Признаки и целевая переменная
X_wine = wine.drop(columns=['quality', 'good']).values
y_wine = wine['good'].values
feature_names = wine.drop(columns=['quality', 'good']).columns

print(wine.head())
print("Размер:", wine.shape)
print("Распределение классов:")
print(wine['good'].value_counts())
""")

md("""### Обучение логистической регрессии и оценка качества""")

code("""from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Разделяем на train/test, чтобы оценить качество.
X_train, X_test, y_train, y_test = train_test_split(
    X_wine, y_wine,
    test_size=0.25,
    random_state=0,
    stratify=y_wine
)

# Логистическая регрессия.
# class_weight='balanced' помогает при дисбалансе классов.
clf = LogisticRegression(max_iter=5000, class_weight='balanced', random_state=0)
clf.fit(X_train, y_train)

# Предсказания и метрики.
y_pred = clf.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\\nConfusion matrix:")
print(confusion_matrix(y_test, y_pred))
print("\\nClassification report:")
print(classification_report(
    y_test, y_pred,
    target_names=['Не качественное', 'Хорошее']
))
""")

md("""### Уравнение гиперплоскости

Обучаем финальную модель на всех данных и выписываем уравнение:

\[
z = b + w_1 x_1 + w_2 x_2 + \\dots + w_n x_n
\]

Класс `"Хорошее"` — если \(z > 0\), иначе `"Не качественное"`.  
Разделяющая гиперповерхность: \(z = 0\).
""")

code("""# Обучаем финальную модель на всех данных, чтобы выписать уравнение гиперплоскости.
final_clf = LogisticRegression(max_iter=5000, class_weight='balanced', random_state=0)
final_clf.fit(X_wine, y_wine)

coef = final_clf.coef_[0]
intercept = final_clf.intercept_[0]

# Собираем уравнение z = b + w1*x1 + ... + wn*xn
terms = [f"{intercept:.6f}"]
for name, c in zip(feature_names, coef):
    terms.append(f"{c:+.6f}*{name}")

equation = " ".join(terms).replace("+ -", "- ")

print("Уравнение гиперплоскости, отделяющей 'Хорошее' от 'Не качественное':")
print(f"z = {equation}")
print("\\nПравило классификации:")
print("  если z > 0 -> 'Хорошее' (1)")
print("  если z <= 0 -> 'Не качественное' (0)")
print("\\nСамо уравнение разделяющей поверхности:")
print(f"{equation} = 0")
""")

# ============================================================
# 5. Сохранение ноутбука
# ============================================================

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.10"
    }
}

nbf.write(nb, "Практическое_занятие_3-4.ipynb")
print("Готово: создан файл 'Практическое_занятие_3-4.ipynb'")
