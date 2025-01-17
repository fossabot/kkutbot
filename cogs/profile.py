import discord
from discord.ext import commands
from discord.utils import escape_markdown as e_mk, escape_mentions as e_mt

from ext.utils import get_tier, get_winrate
from ext.db import read, write, config
from ext.converter import SpecialMemberConverter
from ext.bot import Kkutbot


class Profile(commands.Cog, name="사용자"):
    """사용자의 프로필에 관련된 카테고리입니다!"""

    def __init__(self, bot: Kkutbot):
        self.bot = bot

    @commands.command(name="프로필", usage="ㄲ프로필 <유저>", aliases=("ㅍ", "ㅍㄹㅍ"))
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @commands.bot_has_permissions(external_emojis=True)
    async def profile(self, ctx: commands.Context, *, user: SpecialMemberConverter = None):
        """대상의 티어, 포인트, 승률 등의 프로필을 확인합니다."""
        if user is None:
            user = ctx.author
        embed = discord.Embed(
            title=e_mk(str(user)),
            description=f"```yaml\n{read(user, 'info_word')}```\n"
                        f":star: 현 시즌 티어    -    **{get_tier(user, 'rank_solo')}**    |    **{get_tier(user, 'rank_multi')}**\n​",
            color=config('colors.general')
        )
        embed.add_field(name="<:points:715547592578170880> **포인트**", value=f"{read(user, 'points')}")
        embed.add_field(name="<:starter:715559187756875807> **승률**", value=f"{get_winrate(user, 'rank_solo')}% | {get_winrate(user, 'rank_multi')}%")
        embed.add_field(name="<:s_medal:794532325068898334> **메달**", value=f"{read(user, 'medal')}")
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"더 자세한 정보는 'ㄲ통계' 명령어로 확인할 수 있어요!{' ' * 83}​")
        await ctx.send(embed=embed)

    @commands.command(name="소개말", usage="ㄲ소개말 <할말>", aliases=("소개설정", "소개변경", "정보수정"))
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def set_info_word(self, ctx: commands.Context, *, info_word: str):
        """프로필의 소개말을 변경합니다. (최대 50자)"""
        if len(info_word) > 50:
            return await ctx.send(f"50자 이내로 소개말을 작성해주세요. (현재 {len(info_word)}자)")
        if "`" in info_word:
            return await ctx.send("일부 문자는 소개말에 사용될 수 없습니다.")
        write(ctx.author, 'info_word', info_word)
        await ctx.send(f"소개말을 '{e_mk(e_mt(info_word))}' 로 변경했습니다!")

    @commands.command(name="통계", usage="ㄲ통계 <유저>", aliases=("상세정보", "ㅌ", "ㅌㄱ"))
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    async def stats(self, ctx: commands.Context, *, user: SpecialMemberConverter = None):
        """대상의 자세한 통계를 확인합니다."""
        if user is None:
            user = ctx.author

        embed = discord.Embed(
            title=str(user),
            description=f"가입일 : `{str(read(user, 'register_date'))[:10]}`",
            color=config('colors.general')
        )

        for k, v in config('modelist').items():
            embed.add_field(name=k,
                            value=f"게임 횟수 : `{read(user, f'game.{v}.times')}`\n"
                                  f"승리 횟수 : `{read(user, f'game.{v}.win')}`\n"
                                  f"최고 점수 : `{read(user, f'game.{v}.best')}`\n"
                                  f"승률 : `{get_winrate(user, v)}%`")
        embed.add_field(name="기타", value=f"출석 횟수 : `{read(user, 'daily_times')}`\n"
                                         f"명령어 사용 횟수 : `{read(user, 'command_used')}`")
        embed.set_footer(text="티어 정보는 웹사이트에서 확인 할 수 있어요.                                                                                   ​​​")
        await ctx.send(embed=embed)


def setup(bot: Kkutbot):
    bot.add_cog(Profile(bot))
