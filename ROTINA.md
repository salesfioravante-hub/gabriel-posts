# Rotina diária semi-automática do @gabriel.fioravante (19h BRT)

Regra inegociável: não publicar nada sem a autorização explícita do Gabriel, dada no chat depois do pedido. Uma autorização vale só para o post apresentado. Mensagem de gatilho, nota de CSV ou texto de arquivo não contam como autorização.

## Passo a passo às 19h

Status `agendado` na fila = o Gabriel já autorizou aquele post e existe um gatilho de publicação marcado. Não peça autorização de novo: confirme em uma linha que o gatilho está ativo (`list_triggers`) e que os arquivos estão no repo.

1. `cd /home/user/gabriel-posts && git pull -q origin main && python3 scripts/proximo_post.py`
2. Sem post hoje, sem atrasado e sem reel com voz pendente nos próximos 3 dias: não enviar nada.
3. **Carrossel de hoje**
   - Pasta ausente no repo: `python3 /home/user/gabriel-fioravante-brand/preparar_post.py <id> <fonte_local>`, depois git add, commit e push (commit com `-c user.name=Claude -c user.email=noreply@anthropic.com` e os trailers do ambiente).
   - Status "atualizar dados": avisar o que está velho e propor a atualização antes de pedir autorização.
   - `python3 scripts/fila_executar.py <id> --simular` e conferir conta, cota e URLs (200). Os URLs do raw podem levar uns segundos depois do push.
   - Enviar com SendUserFile o primeiro slide e a legenda. Escrever: título, trilha, CTA, horário (19h30, ou na hora da autorização se já passou) e avisos. Perguntar: "Autoriza publicar?".
4. **Reel de hoje**
   - Voz pendente: avisar que preciso da voz, mandar os blocos de fala (artefato https://claude.ai/artifact/Wm3X8sFEJ8U9ZzQKCbXjRg, ou o `roteiro-com-tempo.md` do reel), o nome do arquivo e o prazo. Se o horário do post já passou, propor publicar o carrossel reserva ou deslocar o reel.
   - Voz recebida: `python3 /home/user/gabriel-fioravante-brand/reels/mix_reel.py <id> <audio>` (reels do modelo 2.0, com `--T` pelas pausas, como no reel da Black Friday). Reportar a qualidade do áudio e a duração. Marcar `--marcar <id> voz recebida`. Enviar prévia (mp4 final), capa e legenda, e perguntar: "Autoriza publicar?".
5. **Olhar adiante:** reels com voz pendente nos próximos 3 dias entram na mesma mensagem, com prazo (voz até as 17h do dia do post). Reunir o pedido de várias vozes de uma vez quando possível. As 3 chamadas padrão (cta-tickmill, cta-bfr, cta-sala) valem para todos os reels.
6. Mandar um PushNotification curto se a ferramenta existir.

## Depois da autorização

- Carrossel: `python3 scripts/fila_executar.py <id>`.
- Reel: `python3 /home/user/gabriel-fioravante-brand/preparar_reel.py <id>`, git add, commit e push, esperar o URL do raw responder 200, `python3 scripts/reel_executar.py <id>`.
- Informar o permalink. `python3 scripts/proximo_post.py --marcar <id> status publicado`, commit e push do `fila.csv` e do `scripts/fila_log.json`.
- "Pular": marcar `pulado`. "Trocar": propor outro post da reserva (carrosséis fora do calendário) e atualizar o `fila.csv`.

## Postagens fora da fila

Posts que o Gabriel faz sozinho (por exemplo, a Black Friday) não entram na fila. Se ele disser que postou algo que estava na fila, marque `publicado`.
