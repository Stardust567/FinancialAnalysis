from jinja2 import Template
import FinancialAnalysis
import date
import time

def makepage(code):
    data = FinancialAnalysis.Data(code)

    # make time web string
    time_list = data.time
    time = ""
    for time_temp in time_list:
        time += "<th >"
        time += time_temp
        time += "</th>"

    # make business data web string
    businessesdata = []
    businesses = []
    business_index = list(data.business_data.keys())
    business_content = list(data.business_data.values())

    # make dsily data web string
    datedata = date.DateData(code)
    dates = []
    date_index = datedata.index
    date_content = datedata.data

    count = 1  # 偶数格子为灰色

    for index in data.index:
        if (count % 2 == 1):
            datatemp = "<tr  class=\"dbrow\"><td>" + index + "</td>"
        else:
            datatemp = "<tr><td>" + index + "</td>"

        for indexdata in data.data_mat[index]:
            temp = "<td>" + str(indexdata) + "</td>"
            datatemp += temp
        datatemp += "</tr>"
        businessesdata.append(datatemp)

        count += 1

    for i in range(0, len(business_index), 2):
        if (count % 2 == 1):
            businesstemp = "<tr  class=\"dbrow\"><td class=\"td_label\">" + business_index[i] + "</td>"
        else:
            businesstemp = "<tr><td class=\"td_label\">" + business_index[i] + "</td>"

        businesstemp += "<td class=\"td_width160\">" + business_content[i] + "</td>"
        if (i < len(business_index) - 1):
            i += 1  # 一行有两格内容
        businesstemp += "<td class=\"td_label keep_line\">" + business_index[i] + "</td>"
        businesstemp += "<td class=\"td_width160\">" + business_content[i] + "</td>"
        businesstemp += "</tr>"
        businesses.append(businesstemp)

        count += 1

    for i in range(0, len(date_index), 6):
        if (count % 2 == 1):
            datetemp = "<tr  class=\"dbrow\"><td class=\"td_label\">" + date_index[i] + "</td>"
        else:
            datetemp = "<tr><td class=\"td_label\">" + date_index[i] + "</td>"

        datetemp += "<td class=\"td_w\">" + date_content[i] + "</td>"
        for j in range(4):
            if (i < len(date_index) - 1):
                i += 1  # 一行有五格内容
            datetemp += "<td class=\"td_label keep_line\">" + date_index[i] + "</td>"
            datetemp += "<td class=\"td_w\">" + date_content[i] + "</td>"

        datetemp += "</tr>"
        dates.append(datetemp)

        count += 1

    template_content = str()
    with open("pagemodel.html", "r", encoding="utf-8") as f:
        template_content = f.read()
    template = Template(template_content)
    render_data = {"businessesdata": businessesdata, "businesses": businesses, "code": code, "dates": dates,
                   "time": time}

    with open(str(data.code) + ".html", "w", encoding="utf-8") as f:
        f.write(template.render(render_data))

if __name__ == '__main__':
    for i in range(1,10):
        code = '%06d' % i
        print(code, time.ctime(time.time()))
        makepage(code)


