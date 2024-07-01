import pvporcupine
import pyaudio
import struct
import time
import os
import re
from dotenv import load_dotenv  
import openai
import time
import requests
from io import BytesIO 


load_dotenv("chat.env")  

os.environ["OPENAI_API_TYPE"] = os.environ["Azure_OPENAI_API_TYPE1"]
os.environ["OPENAI_API_BASE"] = os.environ["Azure_OPENAI_API_BASE1"]
os.environ["OPENAI_API_KEY"] = os.environ["Azure_OPENAI_API_KEY1"]
os.environ["OPENAI_API_VERSION"] = os.environ["Azure_OPENAI_API_VERSION1"]
API_KEY="sk-iStSoyTIhpkDiJSZ53B1A503A0B54cB99a58524a5f72A87f"
BASE_URL="https://one.gptgod.work"
Chat_Deployment=os.environ["Azure_OPENAI_Chat_API_Deployment"]
Whisper_key=os.environ["Azure_Whisper_API_KEY"]
Whisper_endpoint = os.environ["Azure_Whisper_API_Url"]
Azure_speech_key= os.environ["Azure_speech_key"]
Azure_speech_region= os.environ["Azure_speech_region"]
Azure_speech_speaker= os.environ["Azure_speech_speaker"]
WakeupWord = os.environ["WakeupWord"]
WakeupModelFile=os.environ["WakeupModelFile"]
os.environ["AZURE_API_KEY"] =API_KEY
os.environ["AZURE_API_BASE"] =BASE_URL
os.environ["AZURE_API_VERSION"] =os.environ["Azure_OPENAI_API_VERSION1"]

messages = []
openai.api_key =API_KEY
openai.api_base = BASE_URL
openai.api_type = os.environ["OPENAI_API_TYPE"] 
# openai.api_version = os.environ["OPENAI_API_VERSION"]

# Set up Azure Speech-to-Text and Text-to-Speech credentials
speech_key = Azure_speech_key
service_region = Azure_speech_region
#auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "ja-JP","zh-CN"])
lang="zh-CN"
# Creates an instance of a keyword recognition model. Update this to
# The phrase your keyword recognition model triggers on.
keyword = WakeupWord
# Create a local keyword recognizer with the default microphone device for input.
#keyword_recognizer = speechsdk.KeywordRecognizer()
done = False

# Set up the audio configuration
# Create a speech recognizer and start the recognition
unknownCount=0
sysmesg={"role": "system", "content": os.environ["sysprompt_"+lang]}
messages=[]
# Define the speech-to-text function
def speech_to_text(audio_data):
    # Azure 订阅密钥和服务区域
    subscription_key = "2e63688a725b496aac836f7c406e539d"
    service_region = "eastasia"
    voice_lang = "zh-CN"
    # 构造请求的 URL
    url = f"https://{service_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language={voice_lang}"
    
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
        'Accept': 'application/json'
    }

    # 发送 POST 请求到 Azure 语音服务
    response = requests.post(url, headers=headers, data=audio_data)
    response_json = response.json()

    # 检查响应状态并处理结果
    if response.status_code == 200:
        # 成功获得语音识别结果
        if 'DisplayText' in response_json:
            return response_json['DisplayText']
        else:
            return None
    else:
        # 输出错误信息
        print("Error:", response_json.get("error", {}).get("message", "Unknown error"))
        return None

def text_to_speech(text):
    print("文字转语音")

# Define the text-to-speech function
# def text_to_speech(text):
#     # Azure 订阅密钥和服务区域
#     subscription_key = "2e63688a725b496aac836f7c406e539d"
#     service_region = "eastasia"
#     voice_lang = "zh-CN"
#     voice_name = 'zh-CN-XiaoxiaoMultilingualNeural'
#     # 设置 TTS 服务 URL
#     url = f"https://{service_region}.tts.speech.microsoft.com/cognitiveservices/v1"

#     # 构造 SSML 请求体
#     ssml_text = f'''
#     <speak version='1.0' xml:lang='{voice_lang}'>
#         <voice name='{voice_name}'> 
#             <prosody rate='20.00%'>{text}</prosody>
#         </voice>
#     </speak>
#     '''

#     headers = {
#         'Ocp-Apim-Subscription-Key': subscription_key,
#         'Content-Type': 'application/ssml+xml',
#         'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3'  # 输出格式可根据需要调整
#     }

#     # 发送 POST 请求到 Azure TTS
#     response = requests.post(url, headers=headers, data=ssml_text)

#     if response.status_code == 200:
#         # 使用 PyAudio 播放音频
#         p = pyaudio.PyAudio()
#         stream = p.open(format=p.get_format_from_width(2),  # 16-bit PCM
#                         channels=1,
#                         rate=16000,
#                         output=True)
#         # 播放音频数据
#         stream.write(response.content)
#         stream.stop_stream()
#         stream.close()
#         p.terminate()
#         print("Audio playback finished.")
#         return True
#     else:
#         print(f"Error code {response.status_code}: {response.text}")
#         return False

# Define the Azure OpenAI language generation function
def generate_text(prompt):
    global messages
    #global quitReg
    #global pause
    
    messages.append({"role": "user", "content": prompt})
    print("generate_text")
    cont = get_llm_response(messages)
    return cont
    
def get_llm_response(messages):
    print(f"get_llm_response{messages}")
    i=20
    messages_ai = messages[-i:]
    sysmesg={"role": "system", "content": os.environ["sysprompt_"+lang]}  
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-all",  # 确保模型名是正确的
        "messages": [sysmesg]+messages_ai,
        "temperature": 0.6,
        "max_tokens": 500
    }
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=data, headers=headers)
    response_json = response.json()
    
    # print(response_json)

    if 'choices' in response_json and len(response_json['choices']) > 0:
        ai_response_content = response_json['choices'][0]['message']['content']
        return ai_response_content
    else:
        return "Error"
    
def text_filter(response):
    # 屏蔽开头的代码部分
    pattern_code = r'^>.*\n'
    response_cleaned = re.sub(pattern_code, '', response, flags=re.MULTILINE)

    # 屏蔽括号里的参考网址
    pattern_url = r'\[.*?\]'
    response_cleaned = re.sub(pattern_url, '', response_cleaned)
    pattern_url = r'\(.*?\)'
    response_cleaned = re.sub(pattern_url, '', response_cleaned)
    # 屏蔽中文括号里的内容
    pattern_square_brackets = r'【.*?】'
    response_cleaned = re.sub(pattern_square_brackets, '', response_cleaned)
    # 屏蔽 **
    pattern_bold = r'\*\*'
    response_cleaned = re.sub(pattern_bold, '', response_cleaned)

    return response_cleaned

def create_porcupine():
    # 获取当前脚本的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # 构建 .ppn 文件的绝对路径
    ppn_path = os.path.join(current_directory, "Hey-Box_en_linux_v3_0_0.ppn")

    return pvporcupine.create(
        keyword_paths=[ppn_path],
        keywords=["Hey-Box"],
        access_key="rpL3nVDTADVXJZFzwXYxxeoR8bGSY5fn/vfw1dvcoWS+ul2j9etwgw=="
    )

def main_loop():
    p = pyaudio.PyAudio()
    porcupine = create_porcupine()
    audio_stream = p.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        while True:
            print("唤醒我说Hey Box...")
            wait_for_wake_word(porcupine, audio_stream)
            process_conversation(audio_stream, porcupine.sample_rate)
    finally:
        audio_stream.close()
        p.terminate()

def wait_for_wake_word(porcupine, audio_stream):
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        result = porcupine.process(pcm)
        if result >= 0:
            print("唤醒成功!")
            return

def process_conversation(stream, rate):
    print("我在听，请讲...")
    frames = record_conversation(stream)
    audio_data = b''.join(frames)
    text = speech_to_text(audio_data)  # Assuming speech_to_text function exists and takes audio data
    if text:
        print(f"You said: {text}")
        response = generate_text(text)  # Assuming generate_text function exists and takes a string
        filtered_response = text_filter(response)  # Assuming text_filter function exists
        print(f"AI said: {filtered_response}")
        text_to_speech(filtered_response)  # Play back the filtered response

def record_conversation(stream):
    frames = []
    silence_threshold = 500
    silence_duration = 2
    last_sound_time = time.time()

    while True:
        data = stream.read(stream._rate)  # 使用stream的采样率作为帧长度
        frames.append(data)
        amplitude = max(struct.unpack_from("h" * stream._rate, data))
        
        if amplitude < silence_threshold:
            if time.time() - last_sound_time > silence_duration:
                return frames
        else:
            last_sound_time = time.time()

# 主程序入口
main_loop()