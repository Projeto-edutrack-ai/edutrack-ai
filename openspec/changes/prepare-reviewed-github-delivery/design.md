# Design

Clone público separado em review/github-current, base ba810a7c3d0264ae70c63f6fbe5d39ace306594a. Nenhum arquivo exclusivo do GitHub em relação ao ZIP edutrack1 foi identificado no inventário de fontes. As diferenças existentes refletem recursos presentes na base escolhida edutrack1 e correções autorizadas.

Aplicar fontes corrigidas e remover somente arquivos desativados de Classroom e testes exclusivos, mantendo documentação histórica em docs/historico. Gerar git diff staged para aplicar em um clone limpo, sem fabricar autoria de commits. Manter o PR em revisão; não executar merge na main.
