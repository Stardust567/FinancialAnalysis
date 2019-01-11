from jinja2 import Template
import FinancialAnalysis
import time
business_name = []
for i in range(1, 10):
    code = '%06d'%i
    data = FinancialAnalysis.Data(code)
    print(code, time.ctime(time.time()))
    key = ["name", "url"]
    url = "Website/" + data.code
    value = [data.name, url]
    temp = dict(zip(key, value))
    business_name.append(temp)

template_content = str()
with open("homepageModel.html", "r", encoding="utf-8") as f:
    template_content = f.read()
template = Template(template_content)
render_data = {"businesses": business_name}

with open("homepage.html", "w", encoding="utf-8") as f:
    f.write(template.render(render_data))

