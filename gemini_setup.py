import logging
import json
from dotenv import load_dotenv
import os
import google.generativeai as genai
from typing import List, Dict, Optional

# Setup logging for the web app to capture errors and info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# Load environment variables from .env file
try:
    load_dotenv()
    logging.info("Loaded environment variables from .env file.")
except Exception as e:
    logging.error(f"Error loading .env file: {e}")

# Configure the Google Generative AI API
model = None
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logging.error("GOOGLE_API_KEY not found in environment variables.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")  
        logging.info("Google Generative AI API configured and model initialized.")
except Exception as e:
    logging.error(f"Error configuring Google Generative AI API: {e}")

# Knowledge base with your Q&A data
KNOWLEDGE_BASE = {
    "english": [
        {"q": "What is land verification?", "a": "Land verification means checking property documents with the government registry to confirm if the land is genuine and free from disputes."},
        {"q": "Why should I verify land before buying?", "a": "Verification helps you avoid buying fake, stolen, or disputed land."},
        {"q": "How can TrustNest help me verify land?", "a": "TrustNest uses AI tools to check documents and provides access to licensed surveyors and lawyers."},
        {"q": "What documents should I ask for before paying for land?", "a": "You should request the deed of assignment, survey plan, certificate of occupancy (C of O), and receipts."},
        {"q": "How do I know if a land is under government acquisition?", "a": "Check the survey plan at the land registry or use TrustNest's verification tool to confirm."},
        {"q": "What are common land fraud tricks I should watch for?", "a": "Fake documents, multiple sales of the same land, and impersonation of owners."},
        {"q": "What should I do if I discover the land I bought has a dispute?", "a": "Contact a lawyer immediately and file a report with the land registry."},
        {"q": "What rights do tenants have in Nigeria?", "a": "Tenants have the right to a written agreement, fair notice before eviction, and peaceful use of the property."},
        {"q": "What rights do landlords have?", "a": "Landlords have the right to receive rent, regain their property after legal notice, and set reasonable rules."},
        {"q": "Can a landlord evict me without notice?", "a": "No. By law, tenants must receive proper written notice before eviction."},
        {"q": "How can I resolve a land dispute without going to court?", "a": "You can use mediation, arbitration, or community elders before taking legal action."},
        {"q": "What is the role of surveyors in land transactions?", "a": "Surveyors confirm the exact boundaries of land and help prevent encroachment issues."},
        {"q": "Can women legally own land in Nigeria?", "a": "Yes. Nigerian law allows women to own, inherit, and sell land, even if some customs disagree."},
        {"q": "How does TrustNest protect buyers from fraud?", "a": "By pre-screening agents, landlords, and documents before allowing them on the platform."},
        {"q": "What should I do if I am scammed in a land transaction?", "a": "Report to the police, contact a lawyer, and submit your case to TrustNest's dispute awareness tool for guidance."}
    ],
    "yoruba": [
        {"q": "Kini ìfọwọ́sí ilẹ̀?", "a": "Ìfọwọ́sí ilẹ̀ túmọ̀ sí àyẹ̀wò àwọn ìwé ilẹ̀ níbi ìforúkọsílẹ̀ ìjọba láti jẹ́risi pé ilẹ̀ náà jẹ́ òótọ́ àti pé kò ní ìjà."},
        {"q": "Kí ló dé tí mo fi gbọ́dọ̀ fọwọ́sí ilẹ̀ kí n tó rà á?", "a": "Ìfọwọ́sí yóò dá ọ lórí pé o kò ní rà ilẹ̀ ìjẹ̀bú, tí wọ́n ji tàbí tí wọ́n ń jiyàn lórí rẹ̀."},
        {"q": "Báwo ni TrustNest ṣe lè ran mi lọ́wọ́ láti fọwọ́sí ilẹ̀?", "a": "TrustNest ń lo irinṣẹ́ AI láti ṣàyẹ̀wò ìwé ilẹ̀, ó sì ń pèsè àyè fún amòfin àti onímọ̀ ìtọ́jú ilẹ̀."},
        {"q": "Àwọn ìwé wo ni mo yẹ kí n bẹ̀rẹ̀ fún kí n tó san owó ilẹ̀?", "a": "Ìwé Deed of Assignment, survey plan, Certificate of Occupancy (C of O), àti risiti."},
        {"q": "Báwo ni mo ṣe lè mọ̀ pé ilẹ̀ wà lábẹ́ ìtẹ́wọ́gbà ìjọba?", "a": "Ṣàyẹ̀wò survey plan níbi ìforúkọsílẹ̀ ilẹ̀ tàbí lo irinṣẹ́ TrustNest."},
        {"q": "Àwọn ìtan ìjẹ̀bú ilẹ̀ wo ni mo yẹ kí n ṣọ́ra fún?", "a": " Ìwé èké, títà ilẹ̀ kan fún ọ̀pọ̀ ènìyàn, àti ẹni tí ń ṣeránpẹ̀ níbi onílé"},
        {"q": "Kí ni mo yẹ kí n ṣe bí mo bá rí ìjà lórí ilẹ̀ tí mo rà?", "a": "Kan si amòfin lẹ́sẹ̀kẹsẹ̀, kí o sì forúkọsílẹ̀ ẹ̀sùn náà níbi ìjọba ilẹ̀."},
        {"q": "Kí ni ẹ̀tọ́ àwọn alájọṣepọ̀ ilé (tenant) ní Naijíríà?", "a": "Wọ́n ní ẹ̀tọ́ sí ìwé adehun, ìkìlọ̀ ṣáájú kí wọ́n lé wọn jáde, àti ìtẹ́lọ́run láti lo ilé náà."},
        {"q": "Báwo ni mo ṣe lè dá ìjà ilẹ̀ dúró láì lọ sí kóòtù?", "a": "Ìfọ̀rọ̀wérọ̀, ìdájọ́ àgbà, tàbí ìdájọ́ àjọṣe kí o tó lọ sí kóòtù."},
        {"q": "Kí ni ipa àwọn surveyor nínú títà ilẹ̀?", "a": "Wọ́n ń dájú pé ilẹ̀ kò ní ìjà àgbègbè àti pé a mọ́ ìpín rẹ̀ dáadáa."},
        {"q": "Ṣé àwọn obìnrin lè ní ilẹ̀ ní Naijíríà?", "a": "Bẹ́ẹ̀ni. Ofin Naijíríà gba àwọn obìnrin láàyè láti ní, jogún, àti tà ilẹ̀."},
        {"q": "Báwo ni TrustNest ṣe ń dáàbò bo àwọn oníbàárà kúrò ní ìjẹ̀bú?", "a": "Nípa ṣíṣàyẹ̀wò àwọn aṣojú, onílé, àti ìwé ṣáájú kí wọ́n tó jẹ́ kí wọ́n wà lórí pẹpẹ."},
        {"q": "Kí ni mo yẹ kí n ṣe bí wọ́n bá tan mi jẹ ní títà ilẹ̀?", "a": "Jẹ́ kó tán níbi ọlọ́pàá, kan si amòfin, kí o sì lo irinṣẹ́ TrustNest fún ìtòsọ́nà."}
    ],
    "igbo": [
        {"q": "Gịnị bụ nchọpụta ala?", "a": "Nchọpụta ala bụ ịlele akwụkwọ ala n'ụlọ ndekọ gọọmenti iji jide n'aka na ala ahụ bụ eziokwu ma na enweghị esemokwu."},
        {"q": "Gịnị mere m ji kwesị inyocha ala tupu m azụta ya?", "a": "Nchọpụta na-enyere gị aka izere ịzụta ala ụgha, nke e ji, ma ọ bụ nke a na-agba mgba banyere ya."},
        {"q": "Kedu ka TrustNest ga-esi nyere m aka n'ịlele ala?", "a": "TrustNest ji ngwa AI nyochaa akwụkwọ ma jikọọ gị na ndị ọka iwu na ndị nyocha ala."},
        {"q": "Kedu akwụkwọ m ga-arịọ tupu m kwụọ ụgwọ ala?", "a": "Deed of Assignment, survey plan, Certificate of Occupancy (C of O), na risiti."},
        {"q": "Kedu ka m ga-esi mara ma ala dị n'okpuru nchịkọta gọọmenti?", "a": "Lelee survey plan na Land Registry ma ọ bụ jiri ngwa nyocha TrustNest."},
        {"q": "Kedu aghụghọ ndị a na-ejikarị eme ndị na-azụ ala?", "a": "Akwụkwọ ụgha, ire otu ala ugboro ugboro, na imegharị onwe onye nwe ala."},
        {"q": "Kedu ihe m ga-eme ma ọ bụrụ na ala m zụtara nwere esemokwu?", "a": "Kpọtụrụ onye ọka iwu ozugbo, ma kọọ okwu ahụ n'ụlọ ndekọ ala."},
        {"q": "Kedu ikike ndị tenants nwere na Naijiria?", "a": "Ha nwere ikike inwe akwụkwọ nkwekọrịta, nkwupụta tupu a chụpụ ha, na udo iji ihe onwunwe ahụ."},
        {"q": "Kedu ikike ndị landlords nwere?", "a": "Ịnata ụgwọ ụlọ, ịnata ala ha azụ mgbe oge gwụchara, na iweta iwu kwesịrị ekwesị."},
        {"q": "Onye nwe ụlọ nwere ike chụpụ m n'enweghị nkwupụta?", "a": "Mba. Dị ka iwu si kwuo, tenants ga-enweta akwụkwọ nkwupụta tupu achụpụ ha."},
        {"q": "Kedu ka m ga-esi kpebie esemokwu ala n'enweghị kòtù?", "a": "Ị nwere ike jiri ntụgharị okwu, ndị isi obodo, ma ọ bụ ndị ọka ikpe ọdịnala tupu i gawa kòtù."},
        {"q": "Kedu ọrụ ndị surveyor n'ime azụmahịa ala?", "a": "Ha na-ekwenye maka oke ala n'eziokwu ma na-egbochi nsogbu ịbanye n'ala ndị ọzọ."},
        {"q": "Ndị inyom nwere ikike inwe ala na Naijiria?", "a": "Ee. Iwu Naijiria na-enye ụmụ nwanyị ikike inwe, jogbuo, ma ọ bụ ree ala ọbụlagodi ma omenala ụfọdụ kwụghara."},
        {"q": "Kedu ka TrustNest si eche ndị na-azụ ihe pụọ n'aka ndị aghụghọ?", "a": "Site n'ịlele akwụkwọ, ndị nwe ala, na ndị nnọchi anya tupu e nyere ha ohere n'elu ikpo okwu ahụ."},
        {"q": "Kedu ihe m ga-eme ma ọ bụrụ na e jiri aghụghọ mee m n'azụmahịa ala?", "a": "Kọọrọ ndị uwe ojii, kpọtụrụ onye ọka iwu, ma tinye okwu ahụ na ngwa TrustNest maka nduzi."}
    ],
    "hausa": [
        {"q": "Mene ne tantance ƙasa?", "a": "Tantance ƙasa na nufin binciken takardun ƙasa a wurin rajistar gwamnati domin tabbatar da sahihancin ƙasar kuma babu rikici a kanta."},
        {"q": "Me yasa ya kamata in tantance ƙasa kafin in saya?", "a": "Tantancewa na taimaka maka guje wa siyan ƙasar bogi, sata, ko wadda ake rikici a kanta."},
        {"q": "Yaya TrustNest zai taimake ni wajen tantance ƙasa?", "a": "TrustNest na amfani da kayan aikin AI don duba takardu kuma yana haɗa ka da lauyoyi da masu auna ƙasa."},
        {"q": "Wadanne takardu zan nema kafin in biya kuɗin ƙasa?", "a": "Deed of Assignment, survey plan, Certificate of Occupancy (C of O), da rasit."},
        {"q": "Yaya zan san idan ƙasa tana ƙarƙashin mallakar gwamnati?", "a": "Duba survey plan a wurin rajistar ƙasa ko kuma ka yi amfani da kayan aikin TrustNest."},
        {"q": "Waɗanne dabarun zamba ake yawan yi wajen siyar da ƙasa?", "a": "Takardun bogi, sayar da ƙasa ɗaya sau da yawa, da yin kwaikwayon mai ƙasa."},
        {"q": "Me zan yi idan ƙasar da na saya tana da rikici?", "a": "Ka tuntubi lauya nan da nan kuma ka kai rahoto a wurin rajistar ƙasa."},
        {"q": "Waɗanne hakkoki masu haya (tenant) suke da su a Najeriya?", "a": "Suna da haƙƙin samun yarjejeniya ta rubuce, sanarwa kafin a kore su, da zaman lafiya wajen amfani da kadarar."},
        {"q": "Waɗanne hakkoki masu gida suke da su?", "a": "Karɓar kuɗin haya, dawo da kadararsu bayan sanarwa na doka, da sanya ƙa'idoji masu kyau."},
        {"q": "Shin mai gida zai iya kore ni ba tare da sanarwa ba?", "a": "A'a. Bisa doka, tenants dole ne su samu sanarwa ta rubuce kafin a kore su."},
        {"q": "Yaya zan iya warware rikicin ƙasa ba tare da zuwa kotu ba?", "a": "Za ka iya yin sulhu, shiga tsakani, ko tattaunawa da dattawan al'umma kafin ka kai ƙara kotu."},
        {"q": "Mene ne aikin surveyors a harkokin ƙasa?", "a": "Suna tabbatar da iyakar ƙasa yadda ya kamata kuma suna hana rikice-rikicen shiga gonar wani."},
        {"q": "Shin mata suna iya mallakar ƙasa a Najeriya?", "a": "Eh. Dokar Najeriya ta ba mata damar mallaka, gadon ƙasa, da sayarwa duk da cewa wasu al'adu ba su amince ba."},
        {"q": "Yaya TrustNest ke kare masu saya daga zamba?", "a": "Ta hanyar binciken masu gida, wakilai, da takardu kafin su shiga dandali."},
        {"q": "Me zan yi idan aka yaudare ni a cinikin ƙasa?", "a": "Ka kai rahoto ga 'yan sanda, ka tuntubi lauya, sannan ka yi amfani da kayan aikin TrustNest don samun jagora."}
    ]
}

def find_similar_question(user_question: str, language: str = "english") -> Optional[Dict]:
    """
    Find the most similar question in the knowledge base using improved matching
    """
    user_q_lower = user_question.lower()
    language_qa = KNOWLEDGE_BASE.get(language, KNOWLEDGE_BASE["english"])
    
    best_match = None
    max_score = 0
    
    for qa in language_qa:
        question_lower = qa["q"].lower()
        answer_lower = qa["a"].lower()
        
        # Check for keyword matches in both question and answer
        user_words = set(user_q_lower.split())
        qa_words = set(question_lower.split() + answer_lower.split())
        
        # Calculate similarity score
        common_words = user_words.intersection(qa_words)
        if len(user_words.union(qa_words)) > 0:
            score = len(common_words) / len(user_words.union(qa_words))
            
            # Bonus for exact phrase matches
            if any(word in question_lower for word in user_q_lower.split() if len(word) > 3):
                score += 0.2
                
            if score > max_score and score > 0.2:  # Lower threshold for better matching
                max_score = score
                best_match = qa
    
    return best_match

def get_gemini_response(user_input: str, language: str = "english"):
    """
    Main function to get response from Gemini with knowledge base integration
    """
    if not model:
        # Fallback to knowledge base only if Gemini is not available
        similar_qa = find_similar_question(user_input, language)
        if similar_qa:
            return similar_qa["a"]
        return "Sorry, the AI service is not available and I couldn't find a relevant answer in my knowledge base."
    
    try:
        # Find similar question in knowledge base for context
        similar_qa = find_similar_question(user_input, language)
        
        # Create comprehensive prompt for Gemini
        prompt = f"""You are TrustNest Assistant, an expert in Nigerian real estate and land verification. 
        
        Your knowledge base contains the following Q&As:
        """
        
        # Add relevant knowledge base entries
        language_qa = KNOWLEDGE_BASE.get(language, KNOWLEDGE_BASE["english"])
        for qa in language_qa:
            prompt += f"Q: {qa['q']}\nA: {qa['a']}\n\n"
        
        prompt += f"""
        User's question: "{user_input}"
        
        Instructions:
        1. If the question is directly answered in your knowledge base, use that information as the foundation
        2. If it's related but needs expansion, build upon the knowledge base information
        3. If it's a new question about Nigerian real estate, Land titles, survey, land maintainace, land provide helpful, accurate information
        4. Always respond in {language} language
        5. Keep responses conversational and helpful
        6. Mention TrustNest services when relevant
        7. If you're not sure about legal specifics, recommend consulting a lawyer
        8. Give clear, concise answers with practical advice
        9. If you can't find a relevant answer, say "I'm sorry, I couldn't generate a proper response to your question."
        10. Make sure to flow naturally from the user's question to your answer, maintaining context
        11. Keep the tone friendly and professional
        12. Make sure to give an answer based on what the user have been asking on a chat 

        
        Provide a helpful, accurate response:"""
        
        # Generate response with retry logic
        response = model.generate_content(prompt)
        
        if response and response.text:
            logging.info("Gemini response generated successfully")
            return response.text.strip()
        else:
            logging.warning("Empty response from Gemini, falling back to knowledge base")
            if similar_qa:
                return similar_qa["a"]
            return "I'm sorry, I couldn't generate a proper response to your question."
            
    except Exception as e:
        logging.error(f"Error in get_gemini_response(): {e}")
        # Fallback to knowledge base if Gemini fails
        similar_qa = find_similar_question(user_input, language)
        if similar_qa:
            logging.info("Falling back to knowledge base answer")
            return similar_qa["a"]
        return f"Sorry, I encountered an error processing your question. Error: {str(e)}"

def ask_question(question: str, language: str = "english") -> str:
    """
    Main interface function for users to ask questions
    """
    if not question or not question.strip():
        return "Please ask a question about land verification or real estate in Nigeria."
    
    logging.info(f"Processing question in {language}: {question}")
    response = get_gemini_response(question.strip(), language)
    return response

def search_knowledge_base(query: str, language: str = "english") -> List[Dict]:
    """
    Search the knowledge base for relevant Q&As
    """
    query_lower = query.lower()
    language_qa = KNOWLEDGE_BASE.get(language, KNOWLEDGE_BASE["english"])
    results = []
    
    for qa in language_qa:
        if any(word in qa["q"].lower() or word in qa["a"].lower() 
               for word in query_lower.split()):
            results.append(qa)
    
    return results[:5]  # Limit to top 5 results

def get_all_questions(language: str = "english") -> List[str]:
    """
    Get all questions from the knowledge base for a specific language
    """
    language_qa = KNOWLEDGE_BASE.get(language, KNOWLEDGE_BASE["english"])
    return [qa["q"] for qa in language_qa]

def chat_interface():
    """
    Simple command-line chat interface for testing
    """
    print("TrustNest Assistant - Nigerian Real Estate Q&A")
    print("Available languages: english, yoruba, igbo, hausa")
    print("Type 'quit' to exit, 'lang <language>' to change language")
    print("-" * 50)
    
    current_language = "english"
    
    while True:
        try:
            user_input = input(f"\n[{current_language}] Ask a question: ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower().startswith('lang '):
                new_lang = user_input.split(' ', 1)[1].lower()
                if new_lang in KNOWLEDGE_BASE:
                    current_language = new_lang
                    print(f"Language changed to {current_language}")
                else:
                    print("Available languages: english, yoruba, igbo, hausa")
                continue
            elif not user_input:
                print("Please ask a question.")
                continue
            
            # Get response
            response = ask_question(user_input, current_language)
            print(f"\nTrustNest Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

# API simulation for web integration
class TrustNestAPI:
    """
    Simulate API endpoints for web application integration
    """
    
    @staticmethod
    def process_question(data: Dict) -> Dict:
        """
        Process a question from web interface
        Expected data format: {"question": "...", "language": "english"}
        """
        try:
            question = data.get("question", "").strip()
            language = data.get("language", "english").lower()
            
            if not question:
                return {
                    "success": False,
                    "error": "No question provided",
                    "response": ""
                }
            
            if language not in KNOWLEDGE_BASE:
                language = "english"  # Default fallback
            
            response = ask_question(question, language)
            
            return {
                "success": True,
                "error": None,
                "response": response,
                "language": language
            }
            
        except Exception as e:
            logging.error(f"API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, an error occurred processing your question."
            }
    
    @staticmethod
    def get_suggested_questions(language: str = "english") -> Dict:
        """
        Get suggested questions for the UI
        """
        try:
            questions = get_all_questions(language)[:5]  # Get first 5 questions
            return {
                "success": True,
                "questions": questions,
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "questions": []
            }

# Test functions
def test_system():
    """
    Test the entire system with sample questions
    """
    print("Testing TrustNest Q&A System")
    print("=" * 40)
    
    test_questions = [
        ("What is land verification?", "english"),
        ("How can I avoid land fraud?", "english"),
        ("Kini ìfọwọ́sí ilẹ̀?", "yoruba"),
        ("Can women own land in Nigeria?", "english")
    ]
    
    for question, lang in test_questions:
        print(f"\nQuestion ({lang}): {question}")
        response = ask_question(question, lang)
        print(f"Response: {response}")
        print("-" * 30)

def demo_api():
    """
    Demo the API simulation
    """
    print("\nTesting API simulation:")
    
    # Test question processing
    test_data = {
        "question": "How do I verify land documents?",
        "language": "english"
    }
    
    result = TrustNestAPI.process_question(test_data)
    print(f"API Response: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    # Test the system
    print("TrustNest Q&A System Initialized")
    print(f"Model available: {model is not None}")
    print(f"Available languages: {list(KNOWLEDGE_BASE.keys())}")
    
    # Run tests
  #
    
    # Start interactive chat (comment out for web app integration)
    # Uncomment the line below to enable command-line chat
    # chat_interface()