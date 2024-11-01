DEFAULT_CHOICE = 0

CONTRIBUTORS = [
    ["Irene Sam", None],
    ["Blue Shark", None],
    ["Ahmedullah", None],
    ["Viktor Ivanenko", None],
    ["Soumyadeep Bose", None],
    ["Kinsley Gitonga", None],
    ["Mohit Mishra", None],
    ["Gagana M D", None],
    ["Beatrice Kemboi", None],
    ["Jidhnyasa Mahajan", None],
    ["Viktoriia", None],
]

SENTIMENT_TAGS = {
    'LABEL_0': -1,
    'LABEL_1': 0,
    'LABEL_2': 1
}

TEXT_COLOR = {"positive": "green", "neutral": "gray", "negative": "red"}

SPANISH_STOP_WORDS = set([
    'a', 'acá', 'ahí', 'al', 'algo', 'algunas', 'algunos', 'allá', 'allí', 'ambos', 'ante', 'antes', 'aquel', 'aquellas', 
    'aquellos', 'aquí', 'arriba', 'así', 'atras', 'aun', 'aunque', 'bajo', 'bastante', 'bien', 'cada', 'casi', 'cerca', 
    'cierto', 'ciertos', 'como', 'con', 'conmigo', 'contigo', 'contra', 'cual', 'cuales', 'cuando', 'cuanta', 'cuantas', 
    'cuanto', 'cuantos', 'de', 'dejar', 'del', 'demás', 'dentro', 'desde', 'donde', 'dos', 'el', 'él', 'ella', 'ellas', 
    'ellos', 'en', 'encima', 'entonces', 'entre', 'era', 'erais', 'eran', 'eras', 'eres', 'es', 'esa', 'esas', 'ese', 
    'eso', 'esos', 'esta', 'estaba', 'estabais', 'estaban', 'estabas', 'estad', 'estada', 'estadas', 'estado', 'estados', 
    'estamos', 'estando', 'estar', 'estaremos', 'estará', 'estarán', 'estarás', 'estaré', 'estaréis', 'estaría', 'estaríais', 
    'estaríamos', 'estarían', 'estarías', 'estas', 'este', 'estemos', 'esto', 'estos', 'estoy', 'estuve', 'estuviera', 
    'estuvierais', 'estuvieran', 'estuvieras', 'estuvieron', 'estuviese', 'estuvieseis', 'estuviesen', 'estuvieses', 'estuvimos', 
    'estuviste', 'estuvisteis', 'estuviéramos', 'estuviésemos', 'estuvo', 'ex', 'excepto', 'fue', 'fuera', 'fuerais', 'fueran', 
    'fueras', 'fueron', 'fuese', 'fueseis', 'fuesen', 'fueses', 'fui', 'fuimos', 'fuiste', 'fuisteis', 'gran', 'grandes', 'ha', 
    'habéis', 'había', 'habíais', 'habíamos', 'habían', 'habías', 'habida', 'habidas', 'habido', 'habidos', 'habiendo', 'habrá', 
    'habrán', 'habrás', 'habré', 'habréis', 'habría', 'habríais', 'habríamos', 'habrían', 'habrías', 'hace', 'haceis', 'hacemos', 
    'hacen', 'hacer', 'hacerlo', 'hacerme', 'hacernos', 'haceros', 'hacerse', 'haces', 'hacia', 'hago', 'han', 'hasta', 'incluso', 
    'intenta', 'intentais', 'intentamos', 'intentan', 'intentar', 'intentas', 'intento', 'ir', 'jamás', 'junto', 'juntos', 'la', 
    'largo', 'las', 'le', 'les', 'lo', 'los', 'mas', 'me', 'menos', 'mi', 'mía', 'mías', 'mientras', 'mío', 'míos', 'mis', 'misma', 
    'mismas', 'mismo', 'mismos', 'modo', 'mucha', 'muchas', 'muchísima', 'muchísimas', 'muchísimo', 'muchísimos', 'mucho', 'muchos', 
    'muy', 'nada', 'ni', 'ninguna', 'ningunas', 'ninguno', 'ningunos', 'no', 'nos', 'nosotras', 'nosotros', 'nuestra', 'nuestras', 
    'nuestro', 'nuestros', 'nunca', 'os', 'otra', 'otras', 'otro', 'otros', 'para', 'parecer', 'pero', 'poca', 'pocas', 'poco', 
    'pocos', 'podéis', 'podemos', 'poder', 'podría', 'podríais', 'podríamos', 'podrían', 'podrías', 'poner', 'por', 'por qué', 'porque', 
    'primero', 'puede', 'pueden', 'puedo', 'pues', 'que', 'qué', 'querer', 'quien', 'quién', 'quienes', 'quiénes', 'quiere', 'se', 
    'según', 'ser', 'si', 'sí', 'siempre', 'siendo', 'sin', 'sino', 'sobre', 'sois', 'solamente', 'solo', 'somos', 'soy', 'su', 'sus', 
    'también', 'tampoco', 'tan', 'tanto', 'te', 'teneis', 'tenemos', 'tener', 'tengo', 'ti', 'tiempo', 'tiene', 'tienen', 'toda', 
    'todas', 'todavía', 'todo', 'todos', 'tu', 'tú', 'tus', 'un', 'una', 'unas', 'uno', 'unos', 'usa', 'usas', 'usáis', 'usamos', 
    'usan', 'usar', 'usas', 'uso', 'usted', 'ustedes', 'va', 'vais', 'valor', 'vamos', 'van', 'varias', 'varios', 'vaya', 'verdad', 
    'verdadera', 'vosotras', 'vosotros', 'voy', 'vuestra', 'vuestras', 'vuestro', 'vuestros', 'y', 'ya', 'yo'
])

CUSTOM_STOP_WORDS = set([
    'ser', 'haber', 'hacer', 'tener', 'poder', 'ir', 'q', 'si', 'solo', 'saber', 'decir',
    'dar', 'querer', 'ver', 'así', 'sos', 'maje', 'dejar', 'si', 'solo', 'si', 'op', 'vos',
    'cada', 'mismo', 'usted', 'mas', 'pues', 'andar', 'ahora', 'claro', 'nunca', 'quedar', 'pasar',
    'venir', 'poner', 'dio', 'señora', 'señor', 'ahí', 'asi', 'vez', 'jajaja'
])