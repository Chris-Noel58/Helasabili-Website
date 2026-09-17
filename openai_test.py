import os
import traceback
try:
    import openai
except Exception as e:
    print('OPENAI_LIB_MISSING', e)
    raise

print('HAS_KEY', bool(os.environ.get('OPENAI_API_KEY')))
try:
    from openai import OpenAI
except Exception as e:
    print('OPENAI_LIB_MISSING', e)
    raise

print('HAS_KEY', bool(os.environ.get('OPENAI_API_KEY')))
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print('NO_API_KEY')
else:
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role':'user','content':'Please reply briefly: list top 2 features of a typical plot listing.'}],
            max_tokens=80,
            temperature=0.2,
        )
        print('OK')
        try:
            print(resp.choices[0].message.content)
        except Exception:
            print(resp)
    except Exception:
        print('ERR')
        traceback.print_exc()
