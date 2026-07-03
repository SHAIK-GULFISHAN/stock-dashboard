from django.shortcuts import render
import yfinance as yf


def home(request):

    stock = None
    chart_data = None
    error = None

    if request.method == "POST":

        symbol = request.POST.get("symbol").upper()

        try:

            ticker = yf.Ticker(symbol)

            data = ticker.history(period="1mo")


            stock = {
                "symbol": symbol,
                "price": round(data["Close"].iloc[-1], 2),
                "change": round(
                    ((data["Close"].iloc[-1] - data["Close"].iloc[0])
                    / data["Close"].iloc[0]) * 100,
                    2
                )
            }


            chart_data = list(
                zip(
                    data.index.strftime("%d-%m"),
                    data["Close"].round(2)
                )
            )


        except Exception as e:
            print(e)
            error = "Stock not found"


    return render(
        request,
        "stocks/home.html",
        {
            "stock": stock,
            "chart_data": chart_data,
            "error": error
        }
    )