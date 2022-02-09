import nextcord.ui
from datetime import datetime
import json

import tables


def get_name(id, res):
    name = f"{res[int(id)]['title']} {res[int(id)]['year']}"
    return name


# current time
now = datetime.now().time()


class SeriesSelect(nextcord.ui.Select):
    def __init__(self, res, ctx, admin_user):

        # Set the options that will be presented inside the dropdown
        options = []
        for i in range(min(5, len(res))):
            options.append(nextcord.SelectOption(label=get_name(i, res), value=i))

        super().__init__(
            placeholder="Choose a series from the dropdown...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.res = res
        self.ctx = ctx
        self.admin_user = admin_user

    async def callback(self, interaction: nextcord.Interaction):

        await interaction.response.send_message(
            f"You have requested: {get_name(self.values[0],self.res)}"
        )

        pending_request = tables.PendingRequest(
            Title=get_name(self.values[0], self.res),
            requester=self.ctx.author.id,
            requester_name=self.ctx.author.name,
            created=now,
            series_data=json.dumps(self.res[int(self.values[0])], indent=4),
        )
        await pending_request.save()

        await self.admin_user.send(
            f"{self.ctx.author} is requesting {get_name(self.values[0],self.res)}"
        )


class SeriesSelectView(nextcord.ui.View):
    def __init__(self, res, ctx, admin_user):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(SeriesSelect(res, ctx, admin_user))
