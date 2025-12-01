import requests
import json

# test the chat endpoint
def test_chat(question):
    url = "http://localhost:8001/chat"
    payload = {"question": question}

    print(f"\n{'='*60}")
    print(f"question: {question}")
    print('='*60)

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()

        print(f"\nanswer:\n{data['answer']}\n")

        print(f"sources ({len(data['sources'])} documents):")
        for i, source in enumerate(data['sources'], 1):
            print(f"\n  {i}. {source['source_file']} (page {source['page_number']})")
            print(f"     score: {source['relevance_score']:.3f}")
            print(f"     snippet: {source['content_snippet'][:100]}...")
    else:
        print(f"error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # test some questions
    test_chat("how many vacation days do employees get?")
    test_chat("what is the parental leave policy?")
    test_chat("when do employees get paid?")
